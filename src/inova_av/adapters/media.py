from __future__ import annotations

import json
import math
import subprocess
from functools import cached_property
from pathlib import Path
from typing import Any

from inova_av.domain.media import AudioStream, MediaProbe, ProxySettings, VideoStream


class MediaToolError(RuntimeError):
    pass


class LocalMediaTools:
    def __init__(
        self,
        *,
        ffmpeg_path: Path,
        ffprobe_path: Path,
        probe_timeout_seconds: int,
        expected_ffmpeg_prefix: str | None = None,
        expected_ffprobe_prefix: str | None = None,
    ) -> None:
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path
        self.probe_timeout_seconds = probe_timeout_seconds
        self.expected_ffmpeg_prefix = expected_ffmpeg_prefix
        self.expected_ffprobe_prefix = expected_ffprobe_prefix

    @cached_property
    def ffmpeg_version(self) -> str:
        return self._version(self.ffmpeg_path, self.expected_ffmpeg_prefix)

    @cached_property
    def ffprobe_version(self) -> str:
        return self._version(self.ffprobe_path, self.expected_ffprobe_prefix)

    def _version(self, executable: Path, expected_prefix: str | None) -> str:
        if not executable.is_file():
            raise FileNotFoundError(f"Ferramenta de mídia ausente: {executable}")
        try:
            completed = subprocess.run(  # noqa: S603 - executável vem da configuração validada
                [str(executable), "-version"],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
            )
        except subprocess.TimeoutExpired as exc:
            raise MediaToolError(f"Timeout ao consultar {executable.name}") from exc
        first_line = completed.stdout.splitlines()[0] if completed.stdout else ""
        if completed.returncode != 0 or not first_line:
            raise MediaToolError(f"Falha ao consultar {executable.name}")
        if expected_prefix and not first_line.startswith(expected_prefix):
            raise MediaToolError(
                f"Versão incompatível de {executable.name}: esperado prefixo {expected_prefix}"
            )
        return first_line

    def probe(self, path: Path) -> MediaProbe:
        _ = self.ffprobe_version
        command = [
            str(self.ffprobe_path),
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ]
        try:
            completed = subprocess.run(  # noqa: S603 - lista de argumentos, sem shell
                command,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.probe_timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise MediaToolError("FFprobe excedeu o tempo limite") from exc
        if completed.returncode != 0:
            detail = completed.stderr.strip().splitlines()[-1] if completed.stderr.strip() else ""
            raise MediaToolError(f"FFprobe rejeitou a mídia: {detail or 'erro não detalhado'}")
        try:
            payload: dict[str, Any] = json.loads(completed.stdout)
            return self._parse_probe(payload)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise MediaToolError(f"Resposta inválida do FFprobe: {exc}") from exc

    def _parse_probe(self, payload: dict[str, Any]) -> MediaProbe:
        streams = payload.get("streams")
        media_format = payload.get("format")
        if not isinstance(streams, list) or not isinstance(media_format, dict):
            raise ValueError("streams ou format ausente")

        video_streams = [
            stream
            for stream in streams
            if stream.get("codec_type") == "video"
            and not bool((stream.get("disposition") or {}).get("attached_pic"))
        ]
        audio_streams = [stream for stream in streams if stream.get("codec_type") == "audio"]
        if not video_streams or not audio_streams:
            raise ValueError("mídia deve conter ao menos um stream de vídeo e um de áudio")

        video = video_streams[0]
        audio = audio_streams[0]
        duration_value = (
            media_format.get("duration") or video.get("duration") or audio.get("duration")
        )
        duration = self._positive_float(duration_value, "duration")
        size_bytes = self._positive_int(media_format.get("size"), "size")
        bit_rate_value = media_format.get("bit_rate")
        bit_rate = (
            None
            if bit_rate_value in {None, "", "N/A"}
            else self._positive_int(bit_rate_value, "bit_rate")
        )
        frame_rate = str(video.get("avg_frame_rate") or video.get("r_frame_rate") or "")

        return MediaProbe(
            format_name=self._required_string(media_format.get("format_name"), "format_name"),
            duration_seconds=duration,
            size_bytes=size_bytes,
            bit_rate=bit_rate,
            video_stream_count=len(video_streams),
            audio_stream_count=len(audio_streams),
            video=VideoStream(
                stream_index=int(video["index"]),
                codec_name=self._required_string(video.get("codec_name"), "video.codec_name"),
                width=int(video["width"]),
                height=int(video["height"]),
                pixel_format=str(video["pix_fmt"]) if video.get("pix_fmt") else None,
                avg_frame_rate=frame_rate,
            ),
            audio=AudioStream(
                stream_index=int(audio["index"]),
                codec_name=self._required_string(audio.get("codec_name"), "audio.codec_name"),
                sample_rate=self._positive_int(audio.get("sample_rate"), "sample_rate"),
                channels=self._positive_int(audio.get("channels"), "channels"),
                channel_layout=(
                    str(audio["channel_layout"]) if audio.get("channel_layout") else None
                ),
            ),
        )

    @staticmethod
    def _positive_float(value: object, field: str) -> float:
        parsed = float(str(value))
        if not math.isfinite(parsed) or parsed <= 0:
            raise ValueError(f"{field} deve ser positivo e finito")
        return parsed

    @staticmethod
    def _positive_int(value: object, field: str) -> int:
        parsed = int(str(value))
        if parsed <= 0:
            raise ValueError(f"{field} deve ser positivo")
        return parsed

    @staticmethod
    def _required_string(value: object, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} é obrigatório")
        return value

    def create_proxy(self, source: Path, destination: Path, profile: ProxySettings) -> None:
        _ = self.ffmpeg_version
        scale = (
            f"scale=w='min({profile.width},iw)':h='min({profile.height},ih)':"
            "force_original_aspect_ratio=decrease:force_divisible_by=2"
        )
        command = [
            str(self.ffmpeg_path),
            "-v",
            "error",
            "-nostdin",
            "-n",
            "-i",
            str(source),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0",
            "-map_metadata",
            "-1",
            "-vf",
            scale,
            "-r",
            str(profile.fps),
            "-c:v",
            profile.video_codec,
            "-preset",
            profile.preset,
            "-crf",
            str(profile.crf),
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            profile.audio_codec,
            "-b:a",
            profile.audio_bitrate,
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(destination),
        ]
        try:
            completed = subprocess.run(  # noqa: S603 - lista de argumentos, sem shell
                command,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=profile.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            destination.unlink(missing_ok=True)
            raise MediaToolError("FFmpeg excedeu o tempo limite do proxy") from exc
        if completed.returncode != 0 or not destination.is_file():
            destination.unlink(missing_ok=True)
            detail = completed.stderr.strip().splitlines()[-1] if completed.stderr.strip() else ""
            raise MediaToolError(f"Falha ao gerar proxy: {detail or 'erro não detalhado'}")
