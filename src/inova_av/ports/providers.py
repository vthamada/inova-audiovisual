from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Protocol


class StorageProvider(Protocol):
    def put_immutable(self, source: Path, destination: str) -> Mapping[str, Any]: ...


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
