from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Any


@dataclass(frozen=True, slots=True)
class VideoStream:
    stream_index: int
    codec_name: str
    width: int
    height: int
    pixel_format: str | None
    avg_frame_rate: str

    def __post_init__(self) -> None:
        if self.stream_index < 0 or self.width <= 0 or self.height <= 0:
            raise ValueError("Stream de vídeo possui índice ou dimensões inválidas")
        if not self.codec_name:
            raise ValueError("Codec de vídeo ausente")
        try:
            rate = Fraction(self.avg_frame_rate)
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError("Frame rate de vídeo inválido") from exc
        if rate <= 0:
            raise ValueError("Frame rate de vídeo deve ser positivo")


@dataclass(frozen=True, slots=True)
class AudioStream:
    stream_index: int
    codec_name: str
    sample_rate: int
    channels: int
    channel_layout: str | None

    def __post_init__(self) -> None:
        if self.stream_index < 0 or self.sample_rate <= 0 or self.channels <= 0:
            raise ValueError("Stream de áudio possui índice ou parâmetros inválidos")
        if not self.codec_name:
            raise ValueError("Codec de áudio ausente")


@dataclass(frozen=True, slots=True)
class MediaProbe:
    format_name: str
    duration_seconds: float
    size_bytes: int
    bit_rate: int | None
    video_stream_count: int
    audio_stream_count: int
    video: VideoStream
    audio: AudioStream

    def __post_init__(self) -> None:
        if not self.format_name:
            raise ValueError("Formato de mídia ausente")
        if not math.isfinite(self.duration_seconds) or self.duration_seconds <= 0:
            raise ValueError("Duração de mídia deve ser positiva e finita")
        if self.size_bytes <= 0:
            raise ValueError("Mídia vazia")
        if self.bit_rate is not None and self.bit_rate <= 0:
            raise ValueError("Bit rate inválido")
        if self.video_stream_count < 1 or self.audio_stream_count < 1:
            raise ValueError("Mídia deve conter vídeo e áudio")

    def to_document(
        self,
        *,
        source_file: str,
        source_sha256: str,
        generated_at: str,
        ffprobe_version: str,
    ) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "source_file": source_file,
            "source_sha256": source_sha256,
            "generated_at": generated_at,
            "ffprobe_version": ffprobe_version,
            "format": {
                "format_name": self.format_name,
                "duration_seconds": self.duration_seconds,
                "size_bytes": self.size_bytes,
                "bit_rate": self.bit_rate,
            },
            "stream_counts": {
                "video": self.video_stream_count,
                "audio": self.audio_stream_count,
            },
            "video": {
                "stream_index": self.video.stream_index,
                "codec_name": self.video.codec_name,
                "width": self.video.width,
                "height": self.video.height,
                "pixel_format": self.video.pixel_format,
                "avg_frame_rate": self.video.avg_frame_rate,
            },
            "audio": {
                "stream_index": self.audio.stream_index,
                "codec_name": self.audio.codec_name,
                "sample_rate": self.audio.sample_rate,
                "channels": self.audio.channels,
                "channel_layout": self.audio.channel_layout,
            },
        }


@dataclass(frozen=True, slots=True)
class ProxySettings:
    width: int
    height: int
    fps: int
    video_codec: str
    audio_codec: str
    crf: int
    preset: str
    audio_bitrate: str
    timeout_seconds: int

    def __post_init__(self) -> None:
        if min(self.width, self.height, self.fps, self.timeout_seconds) <= 0:
            raise ValueError("Perfil de proxy possui valor não positivo")
        if not 0 <= self.crf <= 51:
            raise ValueError("CRF deve estar entre 0 e 51")
        if not all((self.video_codec, self.audio_codec, self.preset, self.audio_bitrate)):
            raise ValueError("Perfil de proxy incompleto")
