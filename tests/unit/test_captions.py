from __future__ import annotations

import pytest

from inova_av.domain.captions import build_caption_cues, to_srt, to_vtt


def test_captions_preserve_text_order_and_limit_to_two_lines() -> None:
    cues = build_caption_cues(
        [
            {
                "start": 0.0,
                "end": 6.0,
                "text": "Conectamos ideias pessoas oportunidades e instituições do território.",
            }
        ],
        max_line_chars=24,
    )

    assert [cue.text.replace("\n", " ") for cue in cues] == [
        "Conectamos ideias pessoas oportunidades e",
        "instituições do território.",
    ]
    assert all(len(cue.text.splitlines()) <= 2 for cue in cues)
    assert cues[0].start == 0
    assert cues[-1].end == 6
    assert all(left.end == right.start for left, right in zip(cues, cues[1:], strict=False))


def test_caption_serializers_use_valid_timecode_separators() -> None:
    cues = build_caption_cues([{"start": 61.2, "end": 62.5, "text": "Teste."}])

    assert to_srt(cues) == "1\n00:01:01,200 --> 00:01:02,500\nTeste.\n"
    assert to_vtt(cues) == "WEBVTT\n\n00:01:01.200 --> 00:01:02.500\nTeste.\n"


def test_caption_generation_rejects_empty_segment() -> None:
    with pytest.raises(ValueError, match="não pode ser vazio"):
        build_caption_cues([{"start": 0, "end": 1, "text": "   "}])
