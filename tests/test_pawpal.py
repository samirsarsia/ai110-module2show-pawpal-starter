"""Quick tests for the PawPal+ logic layer.

Run with:  python -m pytest
"""

from pawpal_system import Pet, Task


def test_task_completion():
    """Calling mark_complete() should flip the task's status to completed."""
    task = Task("Morning walk", duration_minutes=30, priority="high")

    assert task.completed is False  # starts incomplete

    task.mark_complete()

    assert task.completed is True


def test_task_addition_increases_pet_task_count():
    """Adding a task to a Pet should increase that pet's task count by one."""
    pet = Pet("Mochi", "dog")

    assert len(pet.tasks) == 0  # no tasks yet

    pet.add_task(Task("Feed dog", duration_minutes=10, priority="high"))

    assert len(pet.tasks) == 1
