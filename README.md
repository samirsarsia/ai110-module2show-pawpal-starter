# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Below is the actual terminal output from running the demo script (`python main.py`).
It builds an owner (Jordan) with two pets (Mochi the dog, Whiskers the cat) and
five care tasks, then prints the generated daily plan — evidence the system runs
correctly:

```
====================================================
  Today's Schedule for Jordan
  Time budget: 90 min | starts 08:00
====================================================
  1. 08:00–08:05  Feed cat (Whiskers) [high, 5 min]
       ↳ high-priority task; fit within the remaining 90 min of budget
  2. 08:05–08:15  Feed dog (Mochi) [high, 10 min]
       ↳ high-priority task; fit within the remaining 85 min of budget
  3. 08:15–08:45  Morning walk (Mochi) [high, 30 min]
       ↳ high-priority task; fit within the remaining 75 min of budget
  4. 08:45–09:10  Grooming (Mochi) [medium, 25 min]
       ↳ medium-priority task; fit within the remaining 45 min of budget
  5. 09:10–09:30  Play / enrichment (Whiskers) [low, 20 min]
       ↳ low-priority task; fit within the remaining 20 min of budget
----------------------------------------------------
  5 tasks scheduled, 90 min total.
====================================================
```

## 🧪 Testing PawPal+

Run the automated test suite from the project root:

```bash
python -m pytest
```

### What the tests cover

The suite (`tests/test_pawpal.py`, 12 tests) verifies both happy paths and edge
cases across the logic layer:

- **Basic behavior** — marking a task complete flips its status; adding a task
  increases a pet's task count.
- **Sorting** — `sort_by_time()` returns tasks in chronological order, and tasks
  with no preferred time sort to the end.
- **Recurrence** — completing a *daily* task creates a new one due the next day;
  *weekly* advances by 7 days; *once* tasks do not recur.
- **Conflict detection** — overlapping preferred times are flagged, and
  non-overlapping tasks produce no false warnings.
- **Filtering** — `filter_by_status()` and `filter_by_pet()` return the correct
  subsets.
- **Edge case** — a pet with no tasks produces an empty plan and no conflicts
  (no crash).

### Sample test output

```
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0
collected 12 items

tests/test_pawpal.py ............                                        [100%]

============================== 12 passed in 0.02s ==============================
```

### Confidence Level

⭐⭐⭐⭐☆ (4 / 5)

All 12 tests pass and cover the core scheduling behaviors and their main edge
cases, so I'm confident the sorting, recurrence, conflict-detection, and
filtering logic works as intended. I held back the fifth star because a few
areas aren't yet exercised by tests — most notably the budget-based
`filter_tasks()` dropping over-budget tasks, and the interaction between
conflict detection and the greedy back-to-back plan (see the tradeoff noted in
`reflection.md`).

## 📐 Smarter Scheduling

PawPal+ implements several scheduling behaviors in the logic layer
(`pawpal_system.py`). Each feature and the method that implements it:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by priority | `Scheduler.sort_tasks()` | High priority first, shorter tasks break ties so more fit the budget |
| Sort by time | `Scheduler.sort_by_time()` | Chronological by `preferred_time` ("HH:MM"); untimed tasks trail the end |
| Filter by status | `Scheduler.filter_by_status()` | Keep only completed / not-completed tasks |
| Filter by pet | `Scheduler.filter_by_pet()` | Return just one pet's tasks by name |
| Budget filtering | `Scheduler.filter_tasks()` | Greedily drop tasks that don't fit the remaining time |
| Conflict detection | `Scheduler.detect_conflicts()` | Warns on overlapping time slots; returns messages, never raises |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task()` | Completing a daily/weekly task auto-creates the next occurrence |

### Sorting behavior

- **`Scheduler.sort_by_time()`** orders tasks chronologically by their
  `preferred_time`. The sort key converts each `"HH:MM"` string to
  minutes-since-midnight, so ordering is numeric and robust; tasks without a
  preferred time sort to the end, and priority breaks ties when two tasks share
  a time.
- **`Scheduler.sort_tasks()`** orders by priority (high first), then by shorter
  duration, which lets more tasks fit within a limited time budget.

### Filtering behavior

- **`Scheduler.filter_by_status(tasks, completed)`** returns only the tasks
  whose completion status matches — e.g. "show me everything still to do."
- **`Scheduler.filter_by_pet(pet_name)`** returns just the named pet's tasks, so
  the view can be scoped to one animal.
- **`Scheduler.filter_tasks(tasks, budget)`** greedily keeps tasks that fit the
  remaining time and drops the rest, so the plan never exceeds the owner's
  available minutes.

### Conflict detection logic

- **`Scheduler.detect_conflicts()`** computes each timed, incomplete task's
  `[start, end)` interval (start = `preferred_time`, end = start + duration),
  sorts by start, and flags any task that begins before the previous one ends.
  It notes whether the clash is between the **same pet** or **different pets**,
  and returns a list of human-readable warning strings **instead of raising** —
  so the app can surface the warning and keep running. Untimed tasks float and
  never conflict.

### Recurring task logic

- **`Task.next_occurrence()`** builds the next instance of a recurring task using
  `datetime.timedelta`: `daily` advances the due date by one day, `weekly` by one
  week, and `once` returns `None`. Because it uses real date arithmetic, month,
  year, and leap-year rollovers are handled automatically.
- **`Pet.complete_task(task)`** is where completion and frequency interact: it
  marks the task done and, if the task recurs, appends the freshly generated next
  occurrence to the pet's task list.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
