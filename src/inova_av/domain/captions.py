from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CaptionCue:
    start: float
    end: float
    text: str

    def __post_init__(self) -> None:
        if self.start < 0 or self.end <= self.start:
            raise ValueError("Timecode de legenda inválido")
        if not self.text.strip():
            raise ValueError("Legenda não pode ser vazia")


def build_caption_cues(
    segments: Sequence[Mapping[str, Any]], *, max_line_chars: int = 42
) -> tuple[CaptionCue, ...]:
    """Split literal transcript segments into chronological cues of at most two lines."""

    if max_line_chars < 16:
        raise ValueError("Limite de caracteres por linha deve ser de pelo menos 16")
    cues: list[CaptionCue] = []
    for segment in segments:
        start = float(segment["start"])
        end = float(segment["end"])
        chunks = _two_line_chunks(str(segment["text"]), max_line_chars)
        weights = [max(1, len(chunk.replace("\n", " ").strip())) for chunk in chunks]
        total_weight = sum(weights)
        cursor = start
        for index, (chunk, weight) in enumerate(zip(chunks, weights, strict=True)):
            next_cursor = end if index == len(chunks) - 1 else cursor + (
                (end - start) * weight / total_weight
            )
            cues.append(CaptionCue(start=cursor, end=next_cursor, text=chunk))
            cursor = next_cursor
    return tuple(cues)


def to_srt(cues: Sequence[CaptionCue]) -> str:
    blocks = [
        f"{index}\n{_srt_timecode(cue.start)} --> {_srt_timecode(cue.end)}\n{cue.text}"
        for index, cue in enumerate(cues, start=1)
    ]
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def to_vtt(cues: Sequence[CaptionCue]) -> str:
    blocks = [
        f"{_vtt_timecode(cue.start)} --> {_vtt_timecode(cue.end)}\n{cue.text}"
        for cue in cues
    ]
    return "WEBVTT\n\n" + "\n\n".join(blocks) + ("\n" if blocks else "")


def _two_line_chunks(text: str, max_line_chars: int) -> tuple[str, ...]:
    words = text.split()
    if not words:
        raise ValueError("Segmento de transcript não pode ser vazio para gerar legenda")
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if current and len(candidate) > max_line_chars:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return tuple("\n".join(lines[index : index + 2]) for index in range(0, len(lines), 2))


def _srt_timecode(seconds: float) -> str:
    hours, minutes, whole_seconds, milliseconds = _time_parts(seconds)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},{milliseconds:03d}"


def _vtt_timecode(seconds: float) -> str:
    hours, minutes, whole_seconds, milliseconds = _time_parts(seconds)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}.{milliseconds:03d}"


def _time_parts(seconds: float) -> tuple[int, int, int, int]:
    total_milliseconds = round(seconds * 1000)
    milliseconds = total_milliseconds % 1000
    total_seconds = total_milliseconds // 1000
    whole_seconds = total_seconds % 60
    total_minutes = total_seconds // 60
    minutes = total_minutes % 60
    hours = total_minutes // 60
    return hours, minutes, whole_seconds, milliseconds
