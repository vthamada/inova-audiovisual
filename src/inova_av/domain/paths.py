from __future__ import annotations

from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath


def validate_relative_path(value: str) -> PurePath:
    if not value or "\x00" in value:
        raise ValueError("Caminho relativo vazio ou inválido")
    path = PurePath(value)
    windows_path = PureWindowsPath(value)
    posix_path = PurePosixPath(value)
    if (
        windows_path.is_absolute()
        or bool(windows_path.drive)
        or posix_path.is_absolute()
        or ".." in windows_path.parts
        or ".." in posix_path.parts
    ):
        raise ValueError(f"Caminho deve permanecer relativo à raiz: {value}")
    return path


def resolve_under_root(root: Path, value: str, *, must_exist: bool = False) -> Path:
    relative = validate_relative_path(value)
    resolved_root = root.resolve(strict=True)
    candidate = (resolved_root / relative).resolve(strict=must_exist)
    if not candidate.is_relative_to(resolved_root):
        raise ValueError(f"Caminho escapa da raiz permitida: {value}")
    return candidate
