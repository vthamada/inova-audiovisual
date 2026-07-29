from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from inova_av.adapters.media import LocalMediaTools
from inova_av.domain.media import ProxySettings


def _binary(name: str, configured: str) -> Path | None:
    fixed = Path(configured)
    if fixed.is_file():
        return fixed
    resolved = shutil.which(name)
    return Path(resolved) if resolved else None


def test_real_ffprobe_and_proxy_with_synthetic_media(tmp_path: Path) -> None:
    ffmpeg = _binary("ffmpeg", "C:/ffmpeg/bin/ffmpeg.exe")
    ffprobe = _binary("ffprobe", "C:/ffmpeg/bin/ffprobe.exe")
    if ffmpeg is None or ffprobe is None:
        pytest.skip("FFmpeg/FFprobe não disponíveis neste ambiente")

    source = tmp_path / "synthetic-source.mp4"
    subprocess.run(  # noqa: S603 - binário local resolvido sem shell
        [
            str(ffmpeg),
            "-v",
            "error",
            "-nostdin",
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=320x240:rate=30",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=1000:sample_rate=48000",
            "-t",
            "1",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            str(source),
        ],
        check=True,
        capture_output=True,
        timeout=60,
    )

    tools = LocalMediaTools(
        ffmpeg_path=ffmpeg,
        ffprobe_path=ffprobe,
        probe_timeout_seconds=30,
    )
    source_probe = tools.probe(source)
    assert source_probe.video.codec_name == "h264"
    assert source_probe.audio.codec_name == "aac"
    assert source_probe.video.width == 320
    assert source_probe.video.height == 240

    proxy = tmp_path / "proxy.mp4"
    tools.create_proxy(
        source,
        proxy,
        ProxySettings(
            width=1280,
            height=720,
            fps=30,
            video_codec="libx264",
            audio_codec="aac",
            crf=23,
            preset="veryfast",
            audio_bitrate="128k",
            timeout_seconds=60,
        ),
    )
    proxy_probe = tools.probe(proxy)
    assert proxy_probe.video.width == 320
    assert proxy_probe.video.height == 240
    assert proxy_probe.audio.sample_rate == 48000
    assert abs(proxy_probe.duration_seconds - source_probe.duration_seconds) <= 0.5
