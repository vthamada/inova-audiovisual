from __future__ import annotations

import json
import shutil
import stat
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml

from inova_av.application.ingest import IngestSettings, ProxySettings, ingest_project
from inova_av.domain.media import AudioStream, MediaProbe, VideoStream
from inova_av.schemas.registry import validate_document


@pytest.fixture(autouse=True)
def _restore_fixture_permissions(tmp_path: Path):
    yield
    for path in tmp_path.rglob("*"):
        if path.is_file():
            path.chmod(stat.S_IWRITE)


class FakeMediaTools:
    ffmpeg_version = "ffmpeg synthetic-test"
    ffprobe_version = "ffprobe synthetic-test"

    def __init__(self, *, proxy_error: str | None = None) -> None:
        self.proxy_error = proxy_error
        self.probed: list[Path] = []

    def probe(self, path: Path) -> MediaProbe:
        self.probed.append(path)
        return MediaProbe(
            format_name="mov,mp4,m4a,3gp,3g2,mj2",
            duration_seconds=1.0,
            size_bytes=path.stat().st_size,
            bit_rate=1024,
            video_stream_count=1,
            audio_stream_count=1,
            video=VideoStream(
                stream_index=0,
                codec_name="h264",
                width=320,
                height=240,
                pixel_format="yuv420p",
                avg_frame_rate="30/1",
            ),
            audio=AudioStream(
                stream_index=1,
                codec_name="aac",
                sample_rate=48000,
                channels=2,
                channel_layout="stereo",
            ),
        )

    def create_proxy(self, source: Path, destination: Path, profile: ProxySettings) -> None:
        del profile
        if self.proxy_error:
            raise RuntimeError(self.proxy_error)
        shutil.copyfile(source, destination)


def _settings() -> IngestSettings:
    return IngestSettings(
        allowed_extensions=frozenset({".mp4", ".mov"}),
        max_source_bytes=1024 * 1024,
        min_free_bytes=0,
        copy_chunk_bytes=64 * 1024,
        probe_timeout_seconds=30,
        proxy=ProxySettings(
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


def _project(workspace: Path, project_id: str = "VID-2026-9001") -> Path:
    directory = workspace / "projects" / "projeto com espaços"
    directory.mkdir(parents=True)
    document = {
        "schema_version": "1.0",
        "project_id": project_id,
        "title": "Projeto sintético",
        "editorial": "vozes-do-ecossistema",
        "status": "received",
        "source": {
            "filename": "a-definir.mp4",
            "captured_at": None,
            "location": None,
            "operator": None,
            "sha256": None,
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
    return directory


def _fixed_now() -> datetime:
    return datetime(2026, 7, 29, 19, 30, tzinfo=UTC)


def test_ingest_copies_probes_proxies_and_validates_project(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    project = _project(workspace)
    source = tmp_path / "entrada autorizada.mp4"
    source.write_bytes(b"synthetic-media" * 100)

    result = ingest_project(
        workspace_root=workspace,
        project_directory=project,
        source=source,
        authorized_by="Operador de teste",
        settings=_settings(),
        media_tools=FakeMediaTools(),
        now=_fixed_now,
    )

    assert result.status == "validated"
    stored = project / result.source_file
    assert stored.read_bytes() == source.read_bytes()
    assert stored.stat().st_mode & stat.S_IWUSR == 0
    assert (project / result.proxy_file).is_file()

    updated = yaml.safe_load((project / "project.yaml").read_text(encoding="utf-8"))
    assert updated["status"] == "validated"
    assert updated["source"]["filename"] == source.name
    assert updated["source"]["operator"] == "Operador de teste"
    assert updated["source"]["sha256"] == result.source_sha256

    manifest = json.loads((project / result.manifest_file).read_text(encoding="utf-8"))
    report = json.loads(
        (project / "02_processing" / "technical-report.json").read_text(encoding="utf-8")
    )
    assert validate_document("ingest-manifest", manifest) == []
    assert validate_document("media-probe", report) == []
    assert manifest["authorization"]["confirmed_by"] == "Operador de teste"
    assert manifest["source"]["sha256"] == result.source_sha256
    assert json.loads((project / "audit.jsonl").read_text(encoding="utf-8"))["new_state"] == (
        "validated"
    )
    assert not list(project.glob(".ingest-*"))


def test_invalid_extension_is_quarantined_without_copy(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    project = _project(workspace)
    source = tmp_path / "not-video.txt"
    source.write_text("not a video", encoding="utf-8")

    result = ingest_project(
        workspace_root=workspace,
        project_directory=project,
        source=source,
        authorized_by="Operador de teste",
        settings=_settings(),
        media_tools=FakeMediaTools(),
        now=_fixed_now,
    )

    assert result.status == "quarantined"
    assert result.source_file is None
    assert "extensão não permitida" in result.reason
    assert not (project / "01_inbox").exists()
    manifest = json.loads((project / result.manifest_file).read_text(encoding="utf-8"))
    assert validate_document("ingest-manifest", manifest) == []
    assert manifest["quarantine"]["stage"] == "receive"


def test_proxy_failure_moves_staging_to_quarantine(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    project = _project(workspace)
    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic-media")

    result = ingest_project(
        workspace_root=workspace,
        project_directory=project,
        source=source,
        authorized_by="Operador de teste",
        settings=_settings(),
        media_tools=FakeMediaTools(proxy_error="proxy failed"),
        now=_fixed_now,
    )

    assert result.status == "quarantined"
    assert result.reason == "proxy failed"
    assert not (project / "01_inbox").exists()
    quarantine = project / Path(result.manifest_file).parent
    assert any(path.name.startswith("source-") for path in quarantine.iterdir())
    assert yaml.safe_load((project / "project.yaml").read_text(encoding="utf-8"))[
        "status"
    ] == "quarantined"


def test_existing_destination_is_never_overwritten(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    project = _project(workspace)
    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic-media")
    inbox = project / "01_inbox"
    inbox.mkdir()
    sentinel = inbox / "sentinel.txt"
    sentinel.write_text("preserve", encoding="utf-8")

    result = ingest_project(
        workspace_root=workspace,
        project_directory=project,
        source=source,
        authorized_by="Operador de teste",
        settings=_settings(),
        media_tools=FakeMediaTools(),
        now=_fixed_now,
    )

    assert result.status == "quarantined"
    assert "destino já existe" in result.reason
    assert sentinel.read_text(encoding="utf-8") == "preserve"


def test_project_must_remain_inside_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    project = _project(tmp_path / "outside")
    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic-media")

    with pytest.raises(ValueError, match="fora do workspace"):
        ingest_project(
            workspace_root=workspace,
            project_directory=project,
            source=source,
            authorized_by="Operador de teste",
            settings=_settings(),
            media_tools=FakeMediaTools(),
            now=_fixed_now,
        )

    assert yaml.safe_load((project / "project.yaml").read_text(encoding="utf-8"))[
        "status"
    ] == "received"
