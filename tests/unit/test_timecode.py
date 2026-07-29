from decimal import Decimal

import pytest

from inova_av.domain.timecode import duration, parse_seconds, seconds_to_frame


def test_duration_uses_decimal_without_float_accumulation() -> None:
    assert duration("0.1", "0.3") == Decimal("0.2")


@pytest.mark.parametrize("value", ["-0.1", "NaN", "Infinity", "inválido"])
def test_invalid_seconds_are_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        parse_seconds(value)


def test_seconds_to_frame_uses_floor_at_boundary() -> None:
    assert seconds_to_frame("1.999", 30) == 59
    assert seconds_to_frame("2", 30) == 60
