from __future__ import annotations

from decimal import Decimal, InvalidOperation
from fractions import Fraction


def parse_seconds(value: str | int | float | Decimal) -> Decimal:
    try:
        seconds = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Timecode inválido: {value!r}") from exc
    if not seconds.is_finite() or seconds < 0:
        raise ValueError("Timecode deve ser finito e não negativo")
    return seconds


def duration(start: str | int | float | Decimal, end: str | int | float | Decimal) -> Decimal:
    start_seconds = parse_seconds(start)
    end_seconds = parse_seconds(end)
    if end_seconds <= start_seconds:
        raise ValueError("O timecode final deve ser maior que o inicial")
    return end_seconds - start_seconds


def seconds_to_frame(seconds: str | int | float | Decimal, fps: int) -> int:
    if fps <= 0:
        raise ValueError("FPS deve ser positivo")
    value = parse_seconds(seconds)
    exact = Fraction(value) * fps
    return exact.numerator // exact.denominator
