from __future__ import annotations

from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from inova_av.adapters.transcription import FasterWhisperLocalProvider
from inova_av.ports.providers import TranscriptionRequest


class FakeWhisperModel:
    created: list[dict[str, object]] = []
    requests: list[dict[str, object]] = []

    def __init__(self, path: str, **kwargs: object) -> None:
        self.created.append({"path": path, **kwargs})

    def transcribe(self, audio: str, **kwargs: object):
        self.requests.append({"audio": audio, **kwargs})
        segment = SimpleNamespace(
            start=0.0,
            end=1.5,
            text=" Fala literal. ",
            words=[
                SimpleNamespace(start=0.0, end=0.4, word=" Fala", probability=0.9),
                SimpleNamespace(start=0.5, end=1.5, word=" literal.", probability=0.8),
            ],
        )
        return iter([segment]), SimpleNamespace(language="pt")


def _request(media_path: Path) -> TranscriptionRequest:
    return TranscriptionRequest(
        media_path=media_path,
        language="pt",
        model="small",
        model_revision="synthetic-model-revision",
        device="cpu",
        compute_type="int8",
        local_files_only=True,
        vad_filter=True,
        vad_min_silence_duration_ms=2000,
    )


def test_adapter_uses_local_model_and_preserves_word_timestamps(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model_path = tmp_path / "model"
    model_path.mkdir()
    media_path = tmp_path / "source.mp4"
    media_path.write_bytes(b"synthetic-media")
    module = ModuleType("faster_whisper")
    module.WhisperModel = FakeWhisperModel
    monkeypatch.setitem(__import__("sys").modules, "faster_whisper", module)
    FakeWhisperModel.created.clear()
    FakeWhisperModel.requests.clear()

    provider = FasterWhisperLocalProvider(
        model_path=model_path,
        model="small",
        model_revision="synthetic-model-revision",
        device="cpu",
        compute_type="int8",
        expected_package_version="1.2.1",
    )
    output = provider.transcribe(_request(media_path))

    assert FakeWhisperModel.created == [
        {
            "path": str(model_path.resolve()),
            "device": "cpu",
            "compute_type": "int8",
            "local_files_only": True,
        }
    ]
    assert FakeWhisperModel.requests == [
        {
            "audio": str(media_path),
            "language": "pt",
            "task": "transcribe",
            "word_timestamps": True,
            "vad_filter": True,
            "vad_parameters": {"min_silence_duration_ms": 2000},
        }
    ]
    assert output.provider.package_version == "1.2.1"
    assert output.provider.revision == "synthetic-model-revision"
    assert output.segments == (
        {
            "id": "segment-0001",
            "start": 0.0,
            "end": 1.5,
            "text": " Fala literal. ",
            "confidence": None,
            "words": [
                {"start": 0.0, "end": 0.4, "text": " Fala", "confidence": 0.9},
                {"start": 0.5, "end": 1.5, "text": " literal.", "confidence": 0.8},
            ],
        },
    )


def test_adapter_rejects_network_enabled_request_before_loading_model(tmp_path: Path) -> None:
    model_path = tmp_path / "model"
    model_path.mkdir()
    media_path = tmp_path / "source.mp4"
    media_path.write_bytes(b"synthetic-media")
    provider = FasterWhisperLocalProvider(
        model_path=model_path,
        model="small",
        model_revision="synthetic-model-revision",
        device="cpu",
        compute_type="int8",
        expected_package_version="1.2.1",
    )
    request = _request(media_path)
    request = TranscriptionRequest(
        media_path=request.media_path,
        language=request.language,
        model=request.model,
        model_revision=request.model_revision,
        device=request.device,
        compute_type=request.compute_type,
        local_files_only=False,
        vad_filter=request.vad_filter,
        vad_min_silence_duration_ms=request.vad_min_silence_duration_ms,
    )

    with pytest.raises(ValueError, match="não permite execução com rede"):
        provider.transcribe(request)
