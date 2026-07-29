from __future__ import annotations

import ctypes
import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from inova_av.common import find_repository_root
from inova_av.schemas.registry import load_document


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    required: bool
    ok: bool
    value: str
    path: str | None = None
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class DoctorReport:
    schema_version: str
    ok: bool
    repository: str
    checks: tuple[Check, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "ok": self.ok,
            "repository": self.repository,
            "checks": [asdict(check) for check in self.checks],
        }


def _resolve_tool(root: Path, configured: str) -> Path | None:
    configured_path = Path(configured)
    if configured_path.is_absolute() and configured_path.is_file():
        return configured_path
    local = (root / configured_path).resolve()
    if local.is_file():
        return local
    found = shutil.which(configured)
    return Path(found).resolve() if found else None


def _command(executable: Path, *arguments: str) -> list[str]:
    if executable.suffix.lower() in {".cmd", ".bat"}:
        command_processor = os.environ.get("COMSPEC", r"C:\Windows\System32\cmd.exe")
        return [command_processor, "/d", "/c", str(executable), *arguments]
    return [str(executable), *arguments]


def _version_check(
    root: Path,
    name: str,
    configured: str,
    arguments: tuple[str, ...],
    *,
    required: bool = True,
    expected_prefix: str | None = None,
) -> Check:
    executable = _resolve_tool(root, configured)
    if executable is None:
        return Check(name, required, False, "não encontrado", detail=f"configurado: {configured}")
    try:
        completed = subprocess.run(  # noqa: S603 - executable is resolved from project config
            _command(executable, *arguments),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return Check(name, required, False, "falha de execução", str(executable), str(exc))
    combined = (completed.stdout or completed.stderr).strip()
    first_line = combined.splitlines()[0] if combined else "sem versão"
    compatible = completed.returncode == 0 and (
        expected_prefix is None or first_line.lstrip("v").startswith(expected_prefix)
    )
    detail = None
    if completed.returncode != 0:
        detail = f"exit code {completed.returncode}"
    elif not compatible:
        detail = f"esperado prefixo {expected_prefix}"
    return Check(name, required, compatible, first_line, str(executable), detail)


def _powershell_value(expression: str) -> str:
    powershell = shutil.which("powershell.exe") or shutil.which("powershell")
    if powershell is None:
        return "indisponível"
    try:
        completed = subprocess.run(  # noqa: S603 - PowerShell and expression are internal constants
            [powershell, "-NoProfile", "-NonInteractive", "-Command", expression],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "indisponível"
    return completed.stdout.strip() if completed.returncode == 0 else "indisponível"


def _hyperframes_check(root: Path, configured: str, expected_version: str) -> Check:
    executable = _resolve_tool(root, configured)
    package_manifest = root / "node_modules" / "hyperframes" / "package.json"
    if executable is None or not package_manifest.is_file():
        return Check("hyperframes", True, False, "dependência local ausente", configured)
    try:
        version = json.loads(package_manifest.read_text(encoding="utf-8"))["version"]
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        return Check(
            "hyperframes",
            True,
            False,
            "manifesto inválido",
            str(package_manifest),
            str(exc),
        )
    return Check("hyperframes", True, version == expected_version, str(version), str(executable))


def _browser_check() -> Check:
    root = Path.home() / ".cache" / "hyperframes" / "chrome"
    found = root.is_dir() and any(path.is_file() for path in root.rglob("*.exe"))
    return Check(
        "chrome-headless-shell",
        True,
        found,
        "provisionado" if found else "não provisionado",
        str(root),
    )


def _memory_value() -> str:
    if sys.platform != "win32":
        return "indisponível"

    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("memory_load", ctypes.c_ulong),
            ("total_physical", ctypes.c_ulonglong),
            ("available_physical", ctypes.c_ulonglong),
            ("total_page_file", ctypes.c_ulonglong),
            ("available_page_file", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("available_virtual", ctypes.c_ulonglong),
            ("available_extended_virtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatusEx()
    status.length = ctypes.sizeof(MemoryStatusEx)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        return "indisponível"
    return (
        f"{status.total_physical / 1024**3:.1f} GiB total; "
        f"{status.available_physical / 1024**3:.1f} GiB disponível"
    )


def build_doctor_report(root: Path | None = None) -> DoctorReport:
    repository = root or find_repository_root()
    config = load_document(repository / "config" / "pipeline.yaml")
    tools = config["tools"]
    requirements = config["tool_requirements"]
    checks: list[Check] = [
        Check(
            "platform",
            True,
            sys.platform == "win32",
            f"{platform.system()} {platform.release()} {platform.machine()}",
        ),
        Check(
            "python",
            True,
            sys.version_info[:2] == (3, 12),
            platform.python_version(),
            sys.executable,
            None if sys.version_info[:2] == (3, 12) else "esperado Python 3.12",
        ),
        _version_check(
            repository,
            "node",
            tools["node"],
            ("--version",),
            expected_prefix=requirements["node_prefix"],
        ),
        _version_check(repository, "npm", tools["npm"], ("--version",)),
        _version_check(
            repository,
            "ffmpeg",
            tools["ffmpeg"],
            ("-hide_banner", "-version"),
            expected_prefix=requirements["ffmpeg_prefix"],
        ),
        _version_check(
            repository,
            "ffprobe",
            tools["ffprobe"],
            ("-hide_banner", "-version"),
            expected_prefix=requirements["ffprobe_prefix"],
        ),
        _hyperframes_check(
            repository,
            tools["hyperframes"],
            requirements["hyperframes_version"],
        ),
        _browser_check(),
        Check(
            "network-policy",
            True,
            config.get("network_policy") == "deny_by_default",
            str(config.get("network_policy")),
        ),
        Check(
            "cpu",
            False,
            True,
            f"{os.cpu_count() or 0} processadores lógicos; {platform.processor()}",
        ),
        Check(
            "gpu",
            False,
            True,
            _powershell_value("(Get-CimInstance Win32_VideoController).Name -join '; '")
            or "indisponível",
        ),
        Check(
            "memory",
            False,
            True,
            _memory_value(),
        ),
        Check(
            "disk",
            True,
            shutil.disk_usage(repository).free >= 20 * 1024**3,
            f"{shutil.disk_usage(repository).free / 1024**3:.1f} GiB livres",
            str(repository.anchor),
            "mínimo da fundação: 20 GiB livres",
        ),
    ]
    ok = all(check.ok for check in checks if check.required)
    return DoctorReport("1.0", ok, str(repository), tuple(checks))
