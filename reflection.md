# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

Based on the PawPal+ scenario, a user should be able to perform these three core actions:

1. **Add a pet and owner profile** — The user enters basic information about themselves (the owner) and their pet (name, species, and any care preferences). This establishes who the plan is for and captures the preferences that later influence scheduling.

2. **Add pet care tasks** — The user records the care tasks their pet needs (e.g., a morning walk, feeding, medication, grooming), including at minimum how long each task takes (duration) and how important it is (priority). This builds the pool of tasks the assistant can choose from.

3. **Generate and view today's plan** — The user asks PawPal+ to produce a daily schedule. The system selects and orders tasks based on constraints (time available, priority, owner preferences), then displays the plan clearly and explains why each task was chosen and when it happens.

**a. Initial design**

My initial UML draft (`diagrams/uml_draft.mmd`) used four classes, each with a
single clear responsibility:

- **Task** — represents one unit of pet care work. Holds `title`,
  `duration_minutes`, `priority`, and an optional `preferred_time`. Its
  responsibility is to describe *what* needs to happen and *how important* it is,
  plus small helpers (`priority_score()` for sorting, `fits_within()` to check
  it against a remaining time budget). Implemented as a dataclass since it is a
  pure data record.

- **Pet** — represents an animal that needs care. Holds `name`, `species`, and
  its list of `tasks`. Its responsibility is to own and manage its own tasks
  (`add_task`, `remove_task`, `list_tasks`). Also a dataclass.

- **Owner** — represents the person responsible for care. Holds `name`,
  `available_minutes` (the daily time budget), `preferences`, and a list of
  `pets`. Its responsibility is to model the human constraints that drive
  scheduling — how much time they have and what they prefer — and to own the
  pets. Also a dataclass.

- **Scheduler** — the "logic" class (a plain class, not a dataclass, because it
  is behavior rather than a data record). Its responsibility is to take the
  owner's constraints and the pets' tasks and produce an ordered daily plan
  (`sort_tasks`, `filter_tasks`, `build_plan`). I deliberately kept scheduling
  logic out of the data classes so the algorithm stays isolated and easy to
  unit-test.

The relationships: an **Owner** owns many **Pets**, a **Pet** has many
**Tasks**, and the **Scheduler** uses the Owner (and its pets) as inputs to
produce a plan. I intentionally dropped an earlier idea of separate `Plan` and
`ScheduledTask` classes to avoid over-engineering; `build_plan()` returns a
simple list of dicts that is easy to display in Streamlit and assert on in
tests.

**b. Design changes**

After generating the skeleton, I asked my AI assistant to review
`pawpal_system.py` for missing relationships and logic bottlenecks. Two of its
observations led me to change the design:

1. **The Scheduler ignored the Owner→Pets relationship.** My initial
   `Scheduler(owner, pet, ...)` bound to a single pet, even though `Owner.pets`
   is a list. An owner with two pets could not get one combined plan. I changed
   the Scheduler to be **owner-scoped** — `Scheduler(owner, ...)` — and added a
   `collect_tasks()` method that gathers tasks across *all* of the owner's pets.
   I made this change because it honors the relationship the data model already
   implied and matches the real scenario (an owner planning their whole day, not
   one pet at a time). The plan dicts now also carry a `pet` field so the output
   stays unambiguous when tasks come from different pets.

2. **There was no anchor for real clock times.** `build_plan()` was meant to
   return `start`/`end` times, but nothing in the model said *when the day
   begins*, so those times could not actually be computed. I added a
   `day_start` parameter (default `"08:00"`) to the Scheduler. I chose to make it
   a Scheduler input rather than an Owner attribute because the start time is a
   property of the planning run, not of the person.

I did **not** adopt every suggestion. The review also proposed enforcing
`priority` values with a shared constant/Enum; I noted it as reasonable but
deferred it to the implementation phase rather than complicating the skeleton
now, since I can validate priorities when I actually write `priority_score()`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

One clear tradeoff is that `build_plan()` places tasks **back-to-back from
`day_start`** using a priority-then-duration greedy fit, rather than honoring
each task's `preferred_time` when it actually builds the timeline. Conflict
detection *does* look at preferred times (it flags overlapping
`[start, end)` intervals via `detect_conflicts()`), but the plan itself still
packs tasks sequentially. So the scheduler can warn you that the 08:00 walk and
the 08:00 vet call overlap, yet the generated plan will simply sequence them one
after another instead of resolving the conflict or pinning either to 08:00.

This tradeoff is reasonable for the scenario because the core promise of PawPal+
is "fit the most important care into the time I have today" — a busy owner
mostly cares that high-priority tasks are not dropped, and that the total fits
their budget. A greedy priority fit delivers that simply and predictably, and
runs in O(n log n) (dominated by the sort). Fully honoring preferred times would
turn scheduling into an interval-packing / constraint-satisfaction problem with
many more edge cases (gaps, bumping lower-priority tasks, what to do when two
"must-happen-now" tasks collide). Separating *detection* (cheap, informative)
from *resolution* (complex) lets the tool stay understandable and still give the
owner the information they need to adjust manually. Honoring preferred times in
the plan itself is a natural next iteration (see the "Smarter Scheduling"
stretch), but was a deliberate scope line, not an oversight.

A second, smaller tradeoff worth noting: I kept `detect_conflicts()` as an
explicit indexed loop instead of a denser `zip`-based list comprehension. The
comprehension is more "Pythonic" but harder to read; since both are O(n log n),
I favored the readable version so the logic is easy to follow and debug.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
