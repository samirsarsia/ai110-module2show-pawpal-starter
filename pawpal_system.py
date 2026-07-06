"""PawPal+ logic layer.

All backend classes for the PawPal+ pet care planning app live here. This is
the "logic layer" that the Streamlit UI (app.py) will import and call.

At this stage the file is a skeleton generated from the UML draft
(diagrams/uml_draft.mmd): class names, attributes, and empty method stubs.
Data-holding objects (Task, Pet, Owner) use dataclasses to keep them clean;
the Scheduler is a regular class since it is behavior, not a data record.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single unit of pet care work (e.g., a morning walk)."""

    title: str
    duration_minutes: int
    priority: str = "medium"
    preferred_time: str | None = None

    def priority_score(self) -> int:
        """Return a numeric weight for this task's priority (for sorting)."""
        raise NotImplementedError

    def fits_within(self, remaining_minutes: int) -> bool:
        """Return True if this task fits in the remaining time budget."""
        raise NotImplementedError


@dataclass
class Pet:
    """An animal that needs care."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        raise NotImplementedError

    def list_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        raise NotImplementedError


@dataclass
class Owner:
    """The person responsible for the pet's care."""

    name: str
    available_minutes: int = 0
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Associate a pet with this owner."""
        raise NotImplementedError

    def set_available_time(self, minutes: int) -> None:
        """Set/update the daily time budget."""
        raise NotImplementedError

    def set_preference(self, key: str, value) -> None:
        """Record a scheduling preference."""
        raise NotImplementedError


class Scheduler:
    """Builds a daily plan across all of an owner's pets within their constraints.

    This is where the "smart" behavior lives. It is kept as a plain class (not a
    dataclass) because it represents logic rather than a data record.

    It schedules tasks for every pet the owner has (owner.pets), anchoring the
    plan to a day_start time so build_plan() can compute real clock times.
    """

    def __init__(
        self,
        owner: Owner,
        time_budget: int | None = None,
        day_start: str = "08:00",
    ) -> None:
        self.owner = owner
        # Fall back to the owner's available time if no explicit budget is given.
        self.time_budget = time_budget if time_budget is not None else owner.available_minutes
        # Clock time the day's plan begins from (used to compute start/end slots).
        self.day_start = day_start

    def collect_tasks(self) -> list[Task]:
        """Gather the care tasks across all of the owner's pets."""
        raise NotImplementedError

    def build_plan(self) -> list[dict]:
        """Select and order tasks (across all pets) within the time budget.

        Returns an ordered list of dicts, one per scheduled task, e.g.:
            {"pet": ..., "title": ..., "start": ..., "end": ..., "priority": ..., "reason": ...}
        """
        raise NotImplementedError

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks (e.g., by priority, then duration)."""
        raise NotImplementedError

    def filter_tasks(self, tasks: list[Task], budget: int) -> list[Task]:
        """Drop tasks that don't fit within the remaining time budget."""
        raise NotImplementedError
