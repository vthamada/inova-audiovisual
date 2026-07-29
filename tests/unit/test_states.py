from itertools import pairwise

import pytest

from inova_av.domain.states import ProjectState, can_transition, require_transition


def test_happy_path_requires_all_human_review_states() -> None:
    path = [
        ProjectState.RECEIVED,
        ProjectState.VALIDATED,
        ProjectState.TRANSCRIBED,
        ProjectState.ANALYZED,
        ProjectState.EDIT_PLANNED,
        ProjectState.DRAFT_RENDERED,
        ProjectState.UNDER_REVIEW,
        ProjectState.APPROVED,
        ProjectState.FINAL_RENDERED,
        ProjectState.PUBLISHED,
    ]
    assert all(can_transition(current, target) for current, target in pairwise(path))


def test_draft_cannot_jump_to_published() -> None:
    assert not can_transition(ProjectState.DRAFT_RENDERED, ProjectState.PUBLISHED)
    with pytest.raises(ValueError, match="draft_rendered -> published"):
        require_transition(ProjectState.DRAFT_RENDERED, ProjectState.PUBLISHED)


def test_quarantine_requires_return_to_received() -> None:
    assert can_transition(ProjectState.QUARANTINED, ProjectState.RECEIVED)
    assert not can_transition(ProjectState.QUARANTINED, ProjectState.VALIDATED)
