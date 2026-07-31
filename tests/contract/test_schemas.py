import pytest

from inova_av.common import find_repository_root
from inova_av.schemas.registry import SCHEMA_FILES, load_document, load_schema, validate_document


def test_every_registered_schema_is_valid() -> None:
    for name in SCHEMA_FILES:
        assert load_schema(name)["$schema"].endswith("2020-12/schema")


def test_project_example_is_valid() -> None:
    root = find_repository_root()
    document = load_document(root / "schemas" / "examples" / "project.valid.yaml")
    assert validate_document("project", document) == []


def test_pipeline_configuration_and_asset_registry_are_valid() -> None:
    root = find_repository_root()
    pipeline = load_document(root / "config" / "pipeline.yaml")
    assets = load_document(root / "assets" / "registry.yaml")
    assert validate_document("pipeline-config", pipeline) == []
    assert validate_document("asset-registry", assets) == []


def test_media_probe_rejects_unsafe_path_and_zero_frame_rate() -> None:
    document = {
        "schema_version": "1.0",
        "source_file": "../outside.mp4",
        "source_sha256": "a" * 64,
        "generated_at": "2026-07-29T19:30:00Z",
        "ffprobe_version": "ffprobe test",
        "format": {
            "format_name": "mp4",
            "duration_seconds": 1,
            "size_bytes": 100,
            "bit_rate": None,
        },
        "stream_counts": {"video": 1, "audio": 1},
        "video": {
            "stream_index": 0,
            "codec_name": "h264",
            "width": 320,
            "height": 240,
            "pixel_format": "yuv420p",
            "avg_frame_rate": "0/1",
        },
        "audio": {
            "stream_index": 1,
            "codec_name": "aac",
            "sample_rate": 48000,
            "channels": 2,
            "channel_layout": "stereo",
        },
    }
    paths = {issue.path for issue in validate_document("media-probe", document)}
    assert paths == {"source_file", "video/avg_frame_rate"}


def test_validated_ingest_manifest_requires_complete_artifacts() -> None:
    document = {
        "schema_version": "1.0",
        "run_id": "INGEST-TEST-1",
        "project_id": "VID-2026-0001",
        "status": "validated",
        "started_at": "2026-07-29T19:30:00Z",
        "finished_at": "2026-07-29T19:31:00Z",
        "authorization": {
            "confirmed_by": "Operador",
            "confirmed_at": "2026-07-29T19:30:00Z",
        },
        "source": {
            "original_filename": "source.mp4",
            "size_bytes": 100,
            "sha256": "a" * 64,
            "stored_path": None,
        },
        "technical_report": None,
        "proxy": None,
        "quarantine": None,
        "tool_versions": {"ffmpeg": "ffmpeg test", "ffprobe": "ffprobe test"},
        "warnings": [],
    }
    paths = {issue.path for issue in validate_document("ingest-manifest", document)}
    assert paths == {"source/stored_path", "technical_report", "proxy"}


def test_approved_project_requires_completed_governance() -> None:
    root = find_repository_root()
    document = load_document(root / "schemas" / "examples" / "project.valid.yaml")
    document["status"] = "approved"
    issues = validate_document("project", document)
    assert {issue.path for issue in issues} == {
        "governance",
        "governance/transcript_reviewed",
        "people/0/image_authorization_status",
        "source/sha256",
    }


def test_validated_project_requires_source_checksum() -> None:
    root = find_repository_root()
    document = load_document(root / "schemas" / "examples" / "project.valid.yaml")
    document["status"] = "validated"
    issues = validate_document("project", document)
    assert [(issue.path, issue.message) for issue in issues] == [
        ("source/sha256", "é obrigatório após validação da origem")
    ]


def test_transcript_rejects_overlapping_segments() -> None:
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
            {"id": "s1", "start": 0, "end": 2, "text": "Primeiro."},
            {"id": "s2", "start": 1.5, "end": 3, "text": "Sobreposto."},
        ],
    }
    issues = validate_document("transcript", document)
    assert any(issue.path == "segments/1/start" for issue in issues)


@pytest.mark.parametrize("source", ["../outside.mp4", "C:\\outside.mp4"])
def test_edit_plan_rejects_source_outside_project(source: str) -> None:
    document = {
        "schema_version": "1.0",
        "project_id": "VID-2026-0001",
        "version": 1,
        "target": {
            "format": "vertical",
            "width": 1080,
            "height": 1920,
            "fps": 30,
            "duration_seconds": 1,
        },
        "segments": [
            {
                "source_file": source,
                "in": 0,
                "out": 1,
                "purpose": "hook",
                "transcript_excerpt": "Teste",
            }
        ],
        "overlays": [],
        "captions": {"source": "edit/captions.ass"},
        "approval": {"status": "pending"},
    }
    assert any("source_file" in issue.path for issue in validate_document("edit-plan", document))


def test_final_manifest_requires_approval_hash() -> None:
    document = {
        "schema_version": "1.0",
        "run_id": "RUN-1",
        "project_id": "VID-2026-0001",
        "render_kind": "final",
        "started_at": "2026-07-29T12:00:00-03:00",
        "finished_at": "2026-07-29T12:01:00-03:00",
        "tool_versions": {},
        "inputs": [],
        "outputs": [],
        "commands": [],
        "approval_sha256": None,
    }
    issues = validate_document("render-manifest", document)
    assert [(issue.path, issue.message) for issue in issues] == [
        ("approval_sha256", "é obrigatório no render final")
    ]


def test_render_result_status_and_exit_code_must_agree() -> None:
    invalid = {
        "schema_version": "1.0",
        "request_id": "REQ-1",
        "status": "succeeded",
        "exit_code": 5,
        "artifacts": [],
        "warnings": [],
        "error": None,
    }
    assert validate_document("render-result", invalid)


def test_asset_registry_rejects_duplicate_ids_and_unsafe_paths() -> None:
    asset = {
        "asset_id": "logo",
        "version": "1.0",
        "path": "../logo.svg",
        "sha256": "a" * 64,
        "origin": "Inova",
        "license": "aprovada",
        "approved_by": "Gestora",
        "approved_at": "2026-07-29T12:00:00-03:00",
        "restrictions": [],
    }
    document = {"schema_version": "1.0", "assets": [asset, dict(asset)]}
    paths = {issue.path for issue in validate_document("asset-registry", document)}
    assert paths == {"assets/0/path", "assets/1/asset_id", "assets/1/path"}
