from __future__ import annotations

from collections.abc import Mapping
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from inova_av.ports.providers import (
    TranscriptionOutput,
    TranscriptionProviderIdentity,
    TranscriptionRequest,
)


class TranscriptionDependencyError(RuntimeError):
    """Raised when the local ASR runtime is missing or incompatible."""


class FasterWhisperLocalProvider:
    """Offline faster-whisper adapter with no model download fallback."""

    provider_id = "faster-whisper"
    is_local = True

    def __init__(
        self,
        *,
        model_path: Path,
        model: str,
        model_revision: str,
        device: str,
        compute_type: str,
        expected_package_version: str,
    ) -> None:
        if not model_path.is_dir() or model_path.is_symlink():
            raise ValueError("Modelo local deve ser um diretório regular já provisionado")
        if not model_revision.strip():
            raise ValueError("Revisão do modelo local é obrigatória")
        package_version = _package_version()
        if package_version != expected_package_version:
            raise TranscriptionDependencyError(
                "Versão do faster-whisper diverge da configuração: "
                f"esperada {expected_package_version}, encontrada {package_version}"
            )
        self._model_path = model_path.resolve(strict=True)
        self._identity = TranscriptionProviderIdentity(
            name=self.provider_id,
            package_version=package_version,
            model=model,
            revision=model_revision,
            device=device,
            compute_type=compute_type,
        )

    def transcribe(self, request: TranscriptionRequest) -> TranscriptionOutput:
        if not request.local_files_only:
            raise ValueError("Adapter faster-whisper não permite execução com rede")
        if (
            request.model != self._identity.model
            or request.model_revision != self._identity.revision
            or request.device != self._identity.device
            or request.compute_type != self._identity.compute_type
        ):
            raise ValueError("Request diverge da identidade do provider local")
        if not request.media_path.is_file() or request.media_path.is_symlink():
            raise ValueError("Mídia de trabalho deve ser um arquivo regular")

        whisper_model = _load_whisper_model(
            self._model_path,
            device=request.device,
            compute_type=request.compute_type,
        )
        raw_segments, _ = whisper_model.transcribe(
            str(request.media_path),
            language=request.language,
            task="transcribe",
            word_timestamps=True,
            vad_filter=request.vad_filter,
            vad_parameters={
                "min_silence_duration_ms": request.vad_min_silence_duration_ms,
            },
        )
        segments = tuple(
            _segment_document(index, segment) for index, segment in enumerate(raw_segments, start=1)
        )
        return TranscriptionOutput(provider=self._identity, segments=segments)


def _package_version() -> str:
    try:
        return version("faster-whisper")
    except PackageNotFoundError as exc:
        raise TranscriptionDependencyError(
            "faster-whisper não está instalado no ambiente Python do projeto"
        ) from exc


def _load_whisper_model(model_path: Path, *, device: str, compute_type: str) -> Any:
    try:
        from faster_whisper import WhisperModel  # type: ignore[import-untyped]
    except ImportError as exc:
        raise TranscriptionDependencyError(
            "faster-whisper não está disponível; reinstale as dependências fixadas"
        ) from exc
    return WhisperModel(
        str(model_path),
        device=device,
        compute_type=compute_type,
        local_files_only=True,
    )


def _segment_document(index: int, segment: Any) -> Mapping[str, Any]:
    document: dict[str, Any] = {
        "id": f"segment-{index:04d}",
        "start": float(segment.start),
        "end": float(segment.end),
        "text": str(segment.text),
        "confidence": None,
    }
    words = getattr(segment, "words", None)
    if words is not None:
        document["words"] = [_word_document(word) for word in words]
    return document


def _word_document(word: Any) -> Mapping[str, Any]:
    probability = getattr(word, "probability", None)
    confidence = float(probability) if isinstance(probability, (int, float)) else None
    return {
        "start": float(word.start),
        "end": float(word.end),
        "text": str(word.word),
        "confidence": confidence,
    }
