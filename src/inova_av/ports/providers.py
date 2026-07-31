from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from inova_av.domain.media import MediaProbe, ProxySettings


@dataclass(frozen=True, slots=True)
class CopyResult:
    sha256: str
    size_bytes: int


class StorageProvider(Protocol):
    def put_immutable(
        self, source: Path, destination: Path, chunk_size: int
    ) -> CopyResult: ...


class MediaToolProvider(Protocol):
    @property
    def ffmpeg_version(self) -> str: ...

    @property
    def ffprobe_version(self) -> str: ...

    def probe(self, path: Path) -> MediaProbe: ...

    def create_proxy(self, source: Path, destination: Path, profile: ProxySettings) -> None: ...


@dataclass(frozen=True, slots=True)
class TranscriptionRequest:
    media_path: Path
    language: str
    model: str
    model_revision: str
    device: str
    compute_type: str
    local_files_only: bool
    vad_filter: bool
    vad_min_silence_duration_ms: int


@dataclass(frozen=True, slots=True)
class TranscriptionProviderIdentity:
    name: str
    package_version: str
    model: str
    revision: str | None
    device: str
    compute_type: str

    def to_document(self) -> dict[str, str | None]:
        return {
            "name": self.name,
            "package_version": self.package_version,
            "model": self.model,
            "revision": self.revision,
            "device": self.device,
            "compute_type": self.compute_type,
        }


@dataclass(frozen=True, slots=True)
class TranscriptionOutput:
    provider: TranscriptionProviderIdentity
    segments: Sequence[Mapping[str, Any]]


class TranscriptionProvider(Protocol):
    @property
    def provider_id(self) -> str: ...

    @property
    def is_local(self) -> bool: ...

    def transcribe(self, request: TranscriptionRequest) -> TranscriptionOutput: ...


class EditorialProvider(Protocol):
    @property
    def provider_id(self) -> str: ...

    def analyze(self, transcript: Mapping[str, Any]) -> Mapping[str, Any]: ...


class RenderProvider(Protocol):
    @property
    def provider_id(self) -> str: ...

    def render(self, request: Mapping[str, Any]) -> Mapping[str, Any]: ...
