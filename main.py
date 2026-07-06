"""PawPal+ demo script (terminal testing ground).

Run with:  python main.py

This is a temporary sandbox to verify the logic layer works end-to-end before
wiring it into the Streamlit UI. It builds an owner with two pets and several
tasks, then prints a readable "Today's Schedule".
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    """Create a sample owner with two pets and a handful of care tasks."""
    owner = Owner("Jordan", available_minutes=90)

    dog = Pet("Mochi", "dog")
    cat = Pet("Whiskers", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)

    # At least three tasks, with different preferred times and priorities.
    dog.add_task(Task("Morning walk", 30, "high", preferred_time="08:00"))
    dog.add_task(Task("Feed dog", 10, "high", preferred_time="08:30"))
    cat.add_task(Task("Feed cat", 5, "high", preferred_time="08:15"))
    cat.add_task(Task("Play / enrichment", 20, "low", preferred_time="17:00"))
    dog.add_task(Task("Grooming", 25, "medium", preferred_time="18:00"))

    return owner


def print_schedule(owner: Owner) -> None:
    """Print a clean, aligned 'Today's Schedule' for the owner's pets."""
    scheduler = Scheduler(owner, day_start="08:00")
    plan = scheduler.build_plan()

    print("=" * 52)
    print(f"  Today's Schedule for {owner.name}")
    print(f"  Time budget: {scheduler.time_budget} min | starts {scheduler.day_start}")
    print("=" * 52)

    if not plan:
        print("  (No tasks scheduled.)")
        return

    total = 0
    for i, row in enumerate(plan, start=1):
        total += row["duration_minutes"]
        print(
            f"  {i}. {row['start']}–{row['end']}  "
            f"{row['title']} ({row['pet']}) "
            f"[{row['priority']}, {row['duration_minutes']} min]"
        )
        print(f"       ↳ {row['reason']}")

    print("-" * 52)
    print(f"  {len(plan)} tasks scheduled, {total} min total.")

    # Show anything that didn't fit, so the demo makes the budget visible.
    scheduled_titles = {(row["pet"], row["title"]) for row in plan}
    skipped = [
        (pet.name, task.title)
        for pet in owner.pets
        for task in pet.tasks
        if not task.completed and (pet.name, task.title) not in scheduled_titles
    ]
    if skipped:
        print(f"  Skipped (over budget): " + ", ".join(t for _, t in skipped))
    print("=" * 52)


def main() -> None:
    owner = build_demo_owner()
    print_schedule(owner)


if __name__ == "__main__":
    main()
