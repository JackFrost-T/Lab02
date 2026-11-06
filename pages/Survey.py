"""Collect course names, credits, and weekly study-time estimates."""

from pathlib import Path

import pandas as pd
import streamlit as st


data_path = Path(__file__).resolve().parents[1] / "data.csv"

st.title("Add a course", icon=":material/edit_note:")

with st.form("course_form"):
    course = st.text_input("Course name")
    credits = st.number_input("Credits", min_value=0.0, step=1.0)
    study_hours = st.number_input("Weekly study hours", min_value=0.0, step=1.0)
    submitted = st.form_submit_button("Save course")

if submitted:
    course = course.strip()
    if not course:
        st.error("Enter a course name.")
    else:
        try:
            if data_path.exists() and data_path.stat().st_size > 0:
                entries = pd.read_csv(data_path)
                if not {"Category", "Value"}.issubset(entries.columns):
                    st.error("The CSV must contain Category and Value columns.")
                    st.stop()
                if "Weekly Study Hours" not in entries.columns:
                    entries["Weekly Study Hours"] = pd.NA
            else:
                entries = pd.DataFrame(
                    columns=["Category", "Value", "Weekly Study Hours"]
                )

            entries.loc[len(entries)] = [course, credits, study_hours]
            entries.to_csv(data_path, index=False)
        except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as error:
            st.error(f"Could not save {data_path.name}: {error}")
        else:
            st.success("Course saved.")

st.header("Saved entries")
if not data_path.exists() or data_path.stat().st_size == 0:
    st.info("No courses have been added yet.")
else:
    try:
        current_data_df = pd.read_csv(data_path)
    except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as error:
        st.error(f"Could not read {data_path.name}: {error}")
    else:
        if not {"Category", "Value"}.issubset(current_data_df.columns):
            st.error("The data.csv file must contain 'Category' and 'Value' columns.")
        else:
            st.dataframe(
                current_data_df.rename(
                    columns={
                        "Category": "Course",
                        "Value": "Credits",
                        "Weekly Study Hours": "Weekly study hours",
                    }
                ),
                hide_index=True,
            )
