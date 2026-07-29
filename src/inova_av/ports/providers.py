from __future__ import annotations

from collections.abc import Mapping
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


class TranscriptionProvider(Protocol):
    @property
    def provider_id(self) -> str: ...

    def transcribe(self, audio: Path, parameters: Mapping[str, Any]) -> Mapping[str, Any]: ...


class EditorialProvider(Protocol):
    @property
    def provider_id(self) -> str: ...

    def analyze(self, transcript: Mapping[str, Any]) -> Mapping[str, Any]: ...


class RenderProvider(Protocol):
    @property
    def provider_id(self) -> str: ...

    def render(self, request: Mapping[str, Any]) -> Mapping[str, Any]: ...
