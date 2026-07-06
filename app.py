import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority}
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Set how much time you have today, then generate the plan.")

time_budget = st.number_input(
    "Time available today (minutes)", min_value=5, max_value=600, value=90, step=5
)
day_start = st.text_input("Day starts at (HH:MM)", value="08:00")

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        # Build the logic-layer objects from the UI inputs.
        owner = Owner(owner_name, available_minutes=int(time_budget))
        pet = Pet(pet_name, species)
        owner.add_pet(pet)
        for t in st.session_state.tasks:
            pet.add_task(
                Task(
                    title=t["title"],
                    duration_minutes=int(t["duration_minutes"]),
                    priority=t["priority"],
                )
            )

        scheduler = Scheduler(owner, day_start=day_start)
        plan = scheduler.build_plan()

        st.markdown(f"### 🗓️ Today's plan for {owner.name}")
        if not plan:
            st.info("No tasks fit within the available time.")
        else:
            st.table(
                [
                    {
                        "Start": row["start"],
                        "End": row["end"],
                        "Task": row["title"],
                        "Pet": row["pet"],
                        "Priority": row["priority"],
                        "Minutes": row["duration_minutes"],
                    }
                    for row in plan
                ]
            )

            scheduled_min = sum(row["duration_minutes"] for row in plan)
            st.caption(
                f"{len(plan)} of {len(st.session_state.tasks)} tasks scheduled "
                f"· {scheduled_min} of {int(time_budget)} min used."
            )

            # Explain the reasoning for each scheduled task.
            with st.expander("Why this plan?"):
                for row in plan:
                    st.markdown(f"- **{row['title']}** — {row['reason']}")

            # Show anything that didn't fit the budget.
            scheduled_titles = {row["title"] for row in plan}
            skipped = [
                t["title"] for t in st.session_state.tasks if t["title"] not in scheduled_titles
            ]
            if skipped:
                st.warning("Skipped (over budget): " + ", ".join(skipped))
