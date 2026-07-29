from pathlib import Path

import pytest

from inova_av.domain.paths import resolve_under_root, validate_relative_path


@pytest.mark.parametrize(
    "value",
    ["../segredo.env", "pasta/../../segredo.env", "C:\\Windows\\system.ini", "/etc/passwd"],
)
def test_untrusted_paths_cannot_escape_root(value: str) -> None:
    with pytest.raises(ValueError):
        validate_relative_path(value)


def test_valid_relative_path_resolves_under_root(tmp_path: Path) -> None:
    target = resolve_under_root(tmp_path, "review/preview.mp4")
    assert target == tmp_path / "review" / "preview.mp4"
