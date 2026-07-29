import json
import shutil
from pathlib import Path

from inova_av.cli.main import run
from inova_av.common import find_repository_root


def test_cli_validates_project_example(capsys) -> None:
    root = find_repository_root()
    example = root / "schemas" / "examples" / "project.valid.yaml"
    assert run(["schema", "validate", "project", str(example)]) == 0
    assert capsys.readouterr().out.startswith("OK project:")


def test_cli_rejects_invalid_project(tmp_path: Path, capsys) -> None:
    invalid = tmp_path / "invalid.yaml"
    invalid.write_text("schema_version: '1.0'\n", encoding="utf-8")
    assert run(["schema", "validate", "project", str(invalid)]) == 2
    assert "ERRO" in capsys.readouterr().err


def test_cli_validates_project_directory() -> None:
    root = find_repository_root()
    directory = root / "schemas" / "examples" / "project-directory"
    assert run(["project", "validate", str(directory)]) == 0


def test_cli_emits_valid_normalized_configuration_json(capsys) -> None:
    assert run(["config", "show", "--json"]) == 0
    document = json.loads(capsys.readouterr().out)
    assert document["network_policy"] == "deny_by_default"
    assert document["approval"]["allow_bypass"] is False


def test_project_validation_supports_directory_with_spaces(tmp_path: Path) -> None:
    root = find_repository_root()
    directory = tmp_path / "projeto com espaços"
    directory.mkdir()
    source = root / "schemas" / "examples" / "project.valid.yaml"
    shutil.copyfile(source, directory / "project.yaml")
    assert run(["project", "validate", str(directory)]) == 0
