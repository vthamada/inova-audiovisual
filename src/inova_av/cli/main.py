from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from inova_av import __version__
from inova_av.adapters.media import LocalMediaTools, MediaToolError
from inova_av.adapters.transcription import (
    FasterWhisperLocalProvider,
    TranscriptionDependencyError,
)
from inova_av.application.doctor import build_doctor_report
from inova_av.application.ingest import IngestSettings, ingest_project
from inova_av.application.review import approve_unchanged_transcript
from inova_av.application.transcribe import TranscriptionSettings, transcribe_project
from inova_av.common import find_repository_root
from inova_av.domain.paths import resolve_under_root
from inova_av.schemas.registry import SCHEMA_FILES, load_document, validate_document


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="inova-av", description="Pipeline Audiovisual Inova")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subcommands = parser.add_subparsers(dest="command", required=True)

    doctor = subcommands.add_parser("doctor", help="diagnostica o ambiente sem alterá-lo")
    doctor.add_argument("--json", action="store_true", dest="as_json")

    config = subcommands.add_parser("config", help="operações de configuração")
    config_commands = config.add_subparsers(dest="config_command", required=True)
    config_show = config_commands.add_parser("show", help="mostra a configuração efetiva")
    config_show.add_argument("--json", action="store_true", dest="as_json")

    schema = subcommands.add_parser("schema", help="operações de schema")
    schema_commands = schema.add_subparsers(dest="schema_command", required=True)
    schema_validate = schema_commands.add_parser("validate", help="valida JSON ou YAML")
    schema_validate.add_argument("schema_name", choices=sorted(SCHEMA_FILES))
    schema_validate.add_argument("file", type=Path)

    project = subcommands.add_parser("project", help="operações de projeto")
    project_commands = project.add_subparsers(dest="project_command", required=True)
    project_validate = project_commands.add_parser("validate", help="valida project.yaml")
    project_validate.add_argument("directory", type=Path)
    project_ingest = project_commands.add_parser(
        "ingest", help="copia, valida e cria proxy de uma mídia local autorizada"
    )
    project_ingest.add_argument("directory", type=Path)
    project_ingest.add_argument("source", type=Path)
    project_ingest.add_argument("--authorized-by", required=True)
    project_ingest.add_argument("--json", action="store_true", dest="as_json")
    project_transcribe = project_commands.add_parser(
        "transcribe", help="transcreve uma cópia validada usando provider local offline"
    )
    project_transcribe.add_argument("directory", type=Path)
    project_transcribe.add_argument("--actor", required=True)
    project_transcribe.add_argument("--json", action="store_true", dest="as_json")
    project_review_transcript = project_commands.add_parser(
        "review-transcript",
        help="registra revisao humana de um transcript sem aprovar edicao ou publicacao",
    )
    project_review_transcript.add_argument("directory", type=Path)
    project_review_transcript.add_argument("--reviewer", required=True)
    project_review_transcript.add_argument(
        "--confirm-unchanged",
        action="store_true",
        help="confirma que o revisor comparou e aprovou o texto sem alteracoes",
    )
    project_review_transcript.add_argument("--json", action="store_true", dest="as_json")
    return parser


def _doctor(as_json: bool) -> int:
    report = build_doctor_report()
    if as_json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"Ambiente: {'OK' if report.ok else 'INCOMPLETO'}")
        for check in report.checks:
            marker = "OK" if check.ok else "FALHA"
            requirement = "obrigatório" if check.required else "informativo"
            suffix = f" — {check.detail}" if check.detail else ""
            print(f"[{marker}] {check.name} ({requirement}): {check.value}{suffix}")
    return 0 if report.ok else 3


def _config_show(as_json: bool) -> int:
    root = find_repository_root()
    value: Any = load_document(root / "config" / "pipeline.yaml")
    issues = validate_document("pipeline-config", value)
    if issues:
        raise ValueError("Configuração inválida: " + "; ".join(issue.render() for issue in issues))
    if as_json:
        print(json.dumps(value, ensure_ascii=False, indent=2))
    else:
        print(yaml.safe_dump(value, allow_unicode=True, sort_keys=False).rstrip())
    return 0


def _validate(schema_name: str, path: Path) -> int:
    value = load_document(path.resolve(strict=True))
    issues = validate_document(schema_name, value)
    if issues:
        for issue in issues:
            print(f"ERRO {issue.render()}", file=sys.stderr)
        return 2
    print(f"OK {schema_name}: {path}")
    return 0


def _project_validate(directory: Path) -> int:
    project_file = directory.resolve(strict=True) / "project.yaml"
    if not project_file.is_file():
        raise FileNotFoundError(f"project.yaml não encontrado em {directory}")
    return _validate("project", project_file)


def _configured_tool_path(root: Path, value: str) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else (root / candidate).resolve()


def _project_ingest(
    directory: Path, source: Path, *, authorized_by: str, as_json: bool
) -> int:
    root = find_repository_root()
    value = load_document(root / "config" / "pipeline.yaml")
    if not isinstance(value, dict):
        raise ValueError("Configuração deve conter um objeto")
    issues = validate_document("pipeline-config", value)
    if issues:
        raise ValueError("Configuração inválida: " + "; ".join(i.render() for i in issues))

    ingest_config = value["ingest"]
    if not isinstance(ingest_config, dict):
        raise ValueError("Configuração de ingestão inválida")
    settings = IngestSettings.from_config(ingest_config)
    workspace = resolve_under_root(root, str(value["workspace_root"]), must_exist=True)
    tools = value["tools"]
    requirements = value["tool_requirements"]
    if not isinstance(tools, dict) or not isinstance(requirements, dict):
        raise ValueError("Configuração de ferramentas inválida")
    media_tools = LocalMediaTools(
        ffmpeg_path=_configured_tool_path(root, str(tools["ffmpeg"])),
        ffprobe_path=_configured_tool_path(root, str(tools["ffprobe"])),
        probe_timeout_seconds=settings.probe_timeout_seconds,
        expected_ffmpeg_prefix=str(requirements["ffmpeg_prefix"]),
        expected_ffprobe_prefix=str(requirements["ffprobe_prefix"]),
    )
    try:
        _ = media_tools.ffmpeg_version
        _ = media_tools.ffprobe_version
    except (FileNotFoundError, MediaToolError) as exc:
        print(f"ERRO dependência de mídia: {exc}", file=sys.stderr)
        return 3

    result = ingest_project(
        workspace_root=workspace,
        project_directory=directory,
        source=source,
        authorized_by=authorized_by,
        settings=settings,
        media_tools=media_tools,
    )
    if as_json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    elif result.status == "validated":
        print(
            f"OK ingestão validada: {result.project_id} — "
            f"manifesto {result.manifest_file}"
        )
    else:
        print(
            f"QUARENTENA {result.project_id}: {result.reason} — "
            f"manifesto {result.manifest_file}",
            file=sys.stderr,
        )
    return 0 if result.status == "validated" else 2


def _project_transcribe(directory: Path, *, actor: str, as_json: bool) -> int:
    root = find_repository_root()
    value = load_document(root / "config" / "pipeline.yaml")
    if not isinstance(value, dict):
        raise ValueError("Configuração deve conter um objeto")
    issues = validate_document("pipeline-config", value)
    if issues:
        raise ValueError("Configuração inválida: " + "; ".join(i.render() for i in issues))
    transcription_config = value["transcription"]
    if not isinstance(transcription_config, dict):
        raise ValueError("Configuração de transcrição inválida")
    settings = TranscriptionSettings.from_config(transcription_config)
    model_path = resolve_under_root(
        root, str(transcription_config["model_path"]), must_exist=True
    )
    workspace = resolve_under_root(root, str(value["workspace_root"]), must_exist=True)
    try:
        provider = FasterWhisperLocalProvider(
            model_path=model_path,
            model=settings.model,
            model_revision=settings.model_revision,
            device=settings.device,
            compute_type=settings.compute_type,
            expected_package_version=settings.provider_version,
        )
        result = transcribe_project(
            workspace_root=workspace,
            project_directory=directory,
            actor=actor,
            settings=settings,
            provider=provider,
        )
    except TranscriptionDependencyError as exc:
        print(f"ERRO dependência de transcrição: {exc}", file=sys.stderr)
        return 3
    if as_json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(
            f"OK transcrição criada: {result.project_id} — "
            f"artefato {result.transcript_file}"
        )
    return 0


def _project_review_transcript(
    directory: Path, *, reviewer: str, confirm_unchanged: bool, as_json: bool
) -> int:
    if not confirm_unchanged:
        raise ValueError(
            "Use --confirm-unchanged somente apos comparar o transcript com a midia"
        )
    root = find_repository_root()
    config = load_document(root / "config" / "pipeline.yaml")
    if not isinstance(config, dict):
        raise ValueError("Configuracao deve conter um objeto")
    workspace = resolve_under_root(root, str(config["workspace_root"]), must_exist=True)
    if directory.is_symlink():
        raise ValueError("Diretorio do projeto nao pode ser symlink")
    project = directory.resolve(strict=True)
    if not project.is_relative_to(workspace):
        raise ValueError("Diretorio do projeto esta fora do workspace permitido")
    reviewed_file = approve_unchanged_transcript(
        project_directory=project,
        reviewer=reviewer,
    )
    result = {"status": "reviewed", "reviewed_transcript_file": reviewed_file}
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"OK revisao de transcript registrada: {reviewed_file}")
    return 0


def run(argv: list[str] | None = None) -> int:
    arguments = _build_parser().parse_args(argv)
    if arguments.command == "doctor":
        return _doctor(arguments.as_json)
    if arguments.command == "config" and arguments.config_command == "show":
        return _config_show(arguments.as_json)
    if arguments.command == "schema" and arguments.schema_command == "validate":
        return _validate(arguments.schema_name, arguments.file)
    if arguments.command == "project" and arguments.project_command == "validate":
        return _project_validate(arguments.directory)
    if arguments.command == "project" and arguments.project_command == "ingest":
        return _project_ingest(
            arguments.directory,
            arguments.source,
            authorized_by=arguments.authorized_by,
            as_json=arguments.as_json,
        )
    if arguments.command == "project" and arguments.project_command == "transcribe":
        return _project_transcribe(
            arguments.directory, actor=arguments.actor, as_json=arguments.as_json
        )
    if arguments.command == "project" and arguments.project_command == "review-transcript":
        return _project_review_transcript(
            arguments.directory,
            reviewer=arguments.reviewer,
            confirm_unchanged=arguments.confirm_unchanged,
            as_json=arguments.as_json,
        )
    raise AssertionError("Comando não tratado")


def main() -> None:
    try:
        raise SystemExit(run())
    except (FileNotFoundError, OSError, RuntimeError, ValueError, yaml.YAMLError) as exc:
        print(f"ERRO {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
