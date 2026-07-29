from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from inova_av import __version__
from inova_av.adapters.media import LocalMediaTools, MediaToolError
from inova_av.application.doctor import build_doctor_report
from inova_av.application.ingest import IngestSettings, ingest_project
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
    raise AssertionError("Comando não tratado")


def main() -> None:
    try:
        raise SystemExit(run())
    except (FileNotFoundError, OSError, RuntimeError, ValueError, yaml.YAMLError) as exc:
        print(f"ERRO {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
