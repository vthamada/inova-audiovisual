from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path

from inova_av.ports.providers import CopyResult


class LocalImmutableStorage:
    def put_immutable(self, source: Path, destination: Path, chunk_size: int) -> CopyResult:
        if chunk_size < 64 * 1024:
            raise ValueError("Chunk de cópia deve ter pelo menos 64 KiB")
        if destination.exists():
            raise FileExistsError(f"Destino já existe: {destination.name}")

        digest = hashlib.sha256()
        size_bytes = 0
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            with source.open("rb") as input_stream:
                before = os.fstat(input_stream.fileno())
                with destination.open("xb") as output_stream:
                    while chunk := input_stream.read(chunk_size):
                        output_stream.write(chunk)
                        digest.update(chunk)
                        size_bytes += len(chunk)
                    output_stream.flush()
                    os.fsync(output_stream.fileno())
                after = os.fstat(input_stream.fileno())
        except Exception:
            destination.unlink(missing_ok=True)
            raise

        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            destination.unlink(missing_ok=True)
            raise RuntimeError("Arquivo de origem mudou durante a cópia")
        if size_bytes != before.st_size:
            destination.unlink(missing_ok=True)
            raise RuntimeError("Tamanho copiado diverge da origem")

        destination.chmod(stat.S_IREAD)
        return CopyResult(sha256=digest.hexdigest(), size_bytes=size_bytes)
