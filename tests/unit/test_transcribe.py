from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml

from inova_av.application.transcribe import TranscriptionSettings, transcribe_project
from inova_av.common import find_repository_root
from inova_av.domain.hashing import sha256_file
from inova_av.ports.providers import (
    TranscriptionOutput,
    TranscriptionProviderIdentity,
    TranscriptionRequest,
)
from inova_av.schemas.registry import load_document, validate_document


class FakeTranscriptionProvider:
    provider_id = "faster-whisper"
    is_local = True

    def __init__(self, *, identity: TranscriptionProviderIdentity | None = None) -> None:
        self.identity = identity or TranscriptionProviderIdentity(
            name="faster-whisper",
            package_version="1.2.1",
            model="small",
            revision="synthetic-test",
            device="cpu",
            compute_type="int8",
        )
        self.requests: list[TranscriptionRequest] = []

    def transcribe(self, request: TranscriptionRequest) -> TranscriptionOutput:
        self.requests.append(request)
        return TranscriptionOutput(
            provider=self.identity,
            segments=(
                {
                    "id": "seg-001",
                    "start": 0.0,
                    "end": 2.0,
                    "text": "Transcrição sintética para revisão.",
                    "confidence": 0.91,
                    "words": [
                        {"start": 0.0, "end": 0.7, "text": "Transcrição"},
                        {"start": 0.8, "end": 1.2, "text": "sintética"},
                        {"start": 1.3, "end": 2.0, "text": "revisão"},
                    ],
                },
            ),
        )


def _settings() -> TranscriptionSettings:
    return TranscriptionSettings(
        provider="faster-whisper",
        provider_version="1.2.1",
        model="small",
        model_revision="synthetic-test",
        device="cpu",
        compute_type="int8",
        language="pt",
        local_files_only=True,
        vad_filter=True,
        vad_min_silence_duration_ms=2000,
    )


def _project(workspace: Path) -> Path:
    directory = workspace / "projeto sintético"
    inbox = directory / "01_inbox"
    inbox.mkdir(parents=True)
    source = inbox / "source-0123456789ab.mp4"
    source.write_bytes(b"synthetic-media-authorized-copy")
    source_sha256 = sha256_file(source)
    document = {
        "schema_version": "1.0",
        "project_id": "VID-2026-9002",
        "title": "Projeto sintético de transcrição",
        "editorial": "vozes-do-ecossistema",
        "status": "validated",
        "source": {
            "filename": "original.mp4",
            "captured_at": None,
            "location": None,
            "operator": "Operador de teste",
            "sha256": source_sha256,
        },
        "people": [
            {
                "name": "Pessoa fictícia",
                "role": "Teste",
                "institution": "Instituição fictícia",
                "image_authorization_status": "pending",
            }
        ],
        "publication": {
            "channels": ["instagram_reels"],
            "target_duration_seconds": 60,
            "language": "pt-BR",
        },
        "branding": {"template_version": None, "logo_asset": None},
        "governance": {
            "institutional_review_required": True,
            "legal_review_required": False,
            "transcript_reviewed": False,
            "approved_by": None,
            "approved_at": None,
        },
    }
    (directory / "project.yaml").write_text(
        yaml.safe_dump(document, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    processing = directory / "02_processing"
    processing.mkdir()
    report = {
        "schema_version": "1.0",
        "source_file": "01_inbox/source-0123456789ab.mp4",
        "source_sha256": source_sha256,
        "generated_at": "2026-07-31T12:00:00Z",
        "ffprobe_version": "ffprobe synthetic-test",
        "format": {
            "format_name": "mp4",
            "duration_seconds": 10.0,
            "size_bytes": source.stat().st_size,
            "bit_rate": 1024,
        },
        "stream_counts": {"video": 1, "audio": 1},
        "video": {
            "stream_index": 0,
            "codec_name": "h264",
            "width": 320,
            "height": 240,
            "pixel_format": "yuv420p",
            "avg_frame_rate": "30/1",
        },
        "audio": {
            "stream_index": 1,
            "codec_name": "aac",
            "sample_rate": 48000,
            "channels": 2,
            "channel_layout": "stereo",
        },
    }
    (processing / "technical-report.json").write_text(
        json.dumps(report), encoding="utf-8"
    )
    return directory


def _fixed_now() -> datetime:
    return datetime(2026, 7, 31, 12, 0, tzinfo=UTC)


def test_unprovisioned_model_revision_blocks_transcription_settings() -> None:
    root = find_repository_root()
    pipeline = load_document(root / "config" / "pipeline.yaml")

    with pytest.raises(ValueError, match="Revisão do modelo local"):
        TranscriptionSettings.from_config(
            {**pipeline["transcription"], "model_revision": None}
        )


def test_transcribe_writes_pending_transcript_and_advances_state(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    project = _project(workspace)
    provider = FakeTranscriptionProvider()

    result = transcribe_project(
        workspace_root=workspace,
        project_directory=project,
        actor="Operador de teste",
        settings=_settings(),
        provider=provider,
        now=_fixed_now,
    )

    assert result.transcript_file == "02_processing/transcript.json"
    transcript = json.loads((project / result.transcript_file).read_text(encoding="utf-8"))
    assert validate_document("transcript", transcript) == []
    assert transcript["review"] == {
        "status": "pending",
        "reviewed_by": None,
        "reviewed_at": None,
    }
    assert transcript["source_sha256"] == sha256_file(
        project / "01_inbox" / "source-0123456789ab.mp4"
    )
    assert provider.requests[0].local_files_only is True
    assert provider.requests[0].media_path.name == "source-0123456789ab.mp4"

    updated = yaml.safe_load((project / "project.yaml").read_text(encoding="utf-8"))
    assert updated["status"] == "transcribed"
    assert updated["governance"]["transcript_reviewed"] is False
    event = json.loads((project / "audit.jsonl").read_text(encoding="utf-8"))
    assert event["event_type"] == "transcription_completed"
    assert event["previous_state"] == "validated"
    assert event["new_state"] == "transcribed"
    assert event["artifact_hashes"]["transcript"] == result.transcript_sha256


def test_transcribe_rejects_metadata_divergence_without_writing(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    project = _project(workspace)
    provider = FakeTranscriptionProvider(
        identity=TranscriptionProviderIdentity(
            name="faster-whisper",
            package_version="1.2.1",
            model="medium",
            revision="synthetic-test",
            device="cpu",
            compute_type="int8",
        )
    )

    with pytest.raises(ValueError, match="Metadados retornados"):
        transcribe_project(
            workspace_root=workspace,
            project_directory=project,
            actor="Operador de teste",
            settings=_settings(),
            provider=provider,
            now=_fixed_now,
        )

    assert not (project / "02_processing" / "transcript.json").exists()
    assert yaml.safe_load((project / "project.yaml").read_text(encoding="utf-8"))["status"] == (
        "validated"
    )


def test_transcribe_rejects_segment_outside_validated_media_duration(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    project = _project(workspace)

    class OutOfBoundsProvider(FakeTranscriptionProvider):
        def transcribe(self, request: TranscriptionRequest) -> TranscriptionOutput:
            output = super().transcribe(request)
            return TranscriptionOutput(
                provider=output.provider,
                segments=(
                    {"id": "too-long", "start": 0, "end": 10.1, "text": "Fora da duração."},
                ),
            )

    with pytest.raises(ValueError, match="ultrapassa a duração"):
        transcribe_project(
            workspace_root=workspace,
            project_directory=project,
            actor="Operador de teste",
            settings=_settings(),
            provider=OutOfBoundsProvider(),
            now=_fixed_now,
        )

    assert not (project / "02_processing" / "transcript.json").exists()
    assert yaml.safe_load((project / "project.yaml").read_text(encoding="utf-8"))["status"] == (
        "validated"
    )


def test_transcribe_refuses_existing_transcript(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    project = _project(workspace)
    processing = project / "02_processing"
    (processing / "transcript.json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(FileExistsError, match="não sobrescreve"):
        transcribe_project(
            workspace_root=workspace,
            project_directory=project,
            actor="Operador de teste",
            settings=_settings(),
            provider=FakeTranscriptionProvider(),
            now=_fixed_now,
        )


def test_transcript_rejects_words_outside_segment_and_non_monotonic() -> None:
    document = {
        "schema_version": "1.0",
        "project_id": "VID-2026-0001",
        "version": 1,
        "language": "pt-BR",
        "source_sha256": "a" * 64,
        "provider": {
            "name": "fake",
            "package_version": "1.0.0",
            "model": "fake",
            "revision": None,
            "device": "cpu",
            "compute_type": "int8",
        },
        "review": {"status": "pending", "reviewed_by": None, "reviewed_at": None},
        "segments": [
            {
                "id": "s1",
                "start": 1,
                "end": 2,
                "text": "Teste.",
                "words": [
                    {"start": 0.5, "end": 1.1, "text": "Fora"},
                    {"start": 1.0, "end": 1.5, "text": "Ordem"},
                ],
            }
        ],
    }

    issues = validate_document("transcript", document)
    assert {issue.path for issue in issues} == {
        "segments/0/words/0",
        "segments/0/words/0/start",
        "segments/0/words/1/start",
    }
