from __future__ import annotations

from enum import StrEnum


class ProjectState(StrEnum):
    RECEIVED = "received"
    VALIDATED = "validated"
    TRANSCRIBED = "transcribed"
    ANALYZED = "analyzed"
    EDIT_PLANNED = "edit_planned"
    DRAFT_RENDERED = "draft_rendered"
    UNDER_REVIEW = "under_review"
    CHANGES_REQUESTED = "changes_requested"
    APPROVED = "approved"
    FINAL_RENDERED = "final_rendered"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    QUARANTINED = "quarantined"


ALLOWED_TRANSITIONS: dict[ProjectState, frozenset[ProjectState]] = {
    ProjectState.RECEIVED: frozenset({ProjectState.VALIDATED, ProjectState.QUARANTINED}),
    ProjectState.VALIDATED: frozenset({ProjectState.TRANSCRIBED, ProjectState.QUARANTINED}),
    ProjectState.TRANSCRIBED: frozenset({ProjectState.ANALYZED, ProjectState.CHANGES_REQUESTED}),
    ProjectState.ANALYZED: frozenset({ProjectState.EDIT_PLANNED, ProjectState.CHANGES_REQUESTED}),
    ProjectState.EDIT_PLANNED: frozenset(
        {ProjectState.DRAFT_RENDERED, ProjectState.CHANGES_REQUESTED}
    ),
    ProjectState.DRAFT_RENDERED: frozenset({ProjectState.UNDER_REVIEW}),
    ProjectState.UNDER_REVIEW: frozenset(
        {ProjectState.CHANGES_REQUESTED, ProjectState.APPROVED}
    ),
    ProjectState.CHANGES_REQUESTED: frozenset(
        {
            ProjectState.TRANSCRIBED,
            ProjectState.ANALYZED,
            ProjectState.EDIT_PLANNED,
            ProjectState.DRAFT_RENDERED,
        }
    ),
    ProjectState.APPROVED: frozenset({ProjectState.FINAL_RENDERED}),
    ProjectState.FINAL_RENDERED: frozenset(
        {ProjectState.PUBLISHED, ProjectState.ARCHIVED}
    ),
    ProjectState.PUBLISHED: frozenset({ProjectState.ARCHIVED}),
    ProjectState.ARCHIVED: frozenset(),
    ProjectState.QUARANTINED: frozenset({ProjectState.RECEIVED}),
}


def can_transition(current: ProjectState, target: ProjectState) -> bool:
    return target in ALLOWED_TRANSITIONS[current]


def require_transition(current: ProjectState, target: ProjectState) -> None:
    if not can_transition(current, target):
        raise ValueError(f"Transição inválida: {current.value} -> {target.value}")
