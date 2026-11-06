"""Visualize course credits and study time."""

import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


data_path = Path(__file__).resolve().parents[1] / "data.json"
csv_path = data_path.with_name("data.csv")


def pie_chart(data, title, value_label):
    return (
        alt.Chart(data)
        .mark_arc(innerRadius=45)
        .encode(
            theta=alt.Theta("Value:Q", title=value_label),
            color=alt.Color("Course:N", title="Course"),
            tooltip=[
                alt.Tooltip("Course:N", title="Course"),
                alt.Tooltip("Value:Q", title=value_label),
            ],
        )
        .properties(title=title, height=300)
    )


def bar_chart(data, value_column, title, value_label):
    return (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X(f"{value_column}:Q", title=value_label),
            y=alt.Y("Course:N", title="Course", sort="-x"),
            tooltip=[
                alt.Tooltip("Course:N", title="Course"),
                alt.Tooltip(f"{value_column}:Q", title=value_label, format=".1f"),
            ],
        )
        .properties(title=title, height=max(250, 45 * len(data)))
    )


st.title("Course and credit visuals", icon=":material/analytics:")

try:
    data = json.loads(data_path.read_text(encoding="utf-8"))
    workload = pd.DataFrame(data["data_points"])
except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
    st.error(f"Could not load {data_path.name}: {error}")
    st.stop()

required_columns = {
    "activity",
    "category",
    "credits",
    "assignment_exam_hours",
    "weekly_hours",
}
if not required_columns.issubset(workload.columns):
    st.error("The data.json file is missing required course data.")
    st.stop()

for column in ["credits", "assignment_exam_hours", "weekly_hours"]:
    workload[column] = pd.to_numeric(workload[column], errors="coerce")

workload = workload.loc[
    workload["category"].astype(str).str.casefold() == "course"
].dropna(subset=["activity", "credits", "assignment_exam_hours", "weekly_hours"])
if workload.empty:
    st.error("No valid course data was found in data.json.")
    st.stop()

st.header("Semester data")
metrics = st.columns(3)
metrics[0].metric("Courses", len(workload))
metrics[1].metric("Credits", f"{workload['credits'].sum():g}")
metrics[2].metric("Average weekly hours", f"{workload['weekly_hours'].mean():.1f}")

json_metrics = {
    "Credits": "credits",
    "Assignments and exams": "assignment_exam_hours",
    "Weekly hours": "weekly_hours",
}
if st.session_state.get("json_metric") not in json_metrics:
    st.session_state["json_metric"] = "Weekly hours"
course_names = workload["activity"].astype(str).tolist()
if "json_courses" not in st.session_state:
    st.session_state["json_courses"] = course_names
else:
    st.session_state["json_courses"] = [
        name for name in st.session_state["json_courses"] if name in course_names
    ]

st.header("Courses from data.json")
controls = st.columns(2)
selected_metric = controls[0].selectbox(
    "Compare by", list(json_metrics), key="json_metric"
)
selected_courses = controls[1].multiselect(
    "Courses", course_names, key="json_courses"
)

static_data = workload[["activity", "weekly_hours"]].rename(
    columns={"activity": "Course", "weekly_hours": "Weekly hours"}
)
dynamic_data = (
    workload.loc[
        workload["activity"].astype(str).isin(selected_courses),
        ["activity", json_metrics[selected_metric]],
    ]
    .groupby("activity", as_index=False)
    .sum()
    .rename(
        columns={
            "activity": "Course",
            json_metrics[selected_metric]: "Value",
        }
    )
)

json_charts = st.columns(2)
if selected_courses:
    json_charts[0].altair_chart(
        pie_chart(
            dynamic_data,
            f"{selected_metric} by course",
            selected_metric,
        )
    )
else:
    json_charts[0].info("Select a course to show the chart.")
json_charts[1].altair_chart(
    bar_chart(static_data, "Weekly hours", "Weekly hours by course", "Weekly hours")
)

st.header("Courses from data.csv")
if not csv_path.exists() or csv_path.stat().st_size == 0:
    st.info("Add a course to see the CSV charts.")
    st.stop()

try:
    entries = pd.read_csv(csv_path)
except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as error:
    st.error(f"Could not load {csv_path.name}: {error}")
    st.stop()

if not {"Category", "Value"}.issubset(entries.columns):
    st.error("The data.csv file must contain Category and Value columns.")
    st.stop()

entries = entries.rename(columns={"Category": "Course", "Value": "Credits"})
entries["Course"] = entries["Course"].astype("string").str.strip()
entries["Credits"] = pd.to_numeric(entries["Credits"], errors="coerce")
credit_data = entries.dropna(subset=["Course", "Credits"])
credit_data = credit_data.loc[
    credit_data["Course"].ne("") & credit_data["Credits"].ge(0)
].groupby("Course", as_index=False)["Credits"].sum()
credit_data = credit_data.rename(columns={"Credits": "Value"})

if credit_data.empty:
    st.info("No valid course credits were found in data.csv.")
    st.stop()

study_data = entries.copy()
if "Weekly Study Hours" not in study_data.columns:
    study_data["Weekly Study Hours"] = pd.NA
study_data["Weekly Study Hours"] = pd.to_numeric(
    study_data["Weekly Study Hours"], errors="coerce"
)
study_data = study_data.dropna(subset=["Course", "Weekly Study Hours"])
study_data = study_data.loc[
    study_data["Course"].ne("")
    & study_data["Weekly Study Hours"].ge(0)
    & study_data["Weekly Study Hours"].lt(float("inf"))
]
study_data = study_data.groupby("Course", as_index=False)["Weekly Study Hours"].mean()

charts = st.columns(2)
charts[0].altair_chart(
    pie_chart(credit_data, "Credits by submitted course", "Credits")
)

if study_data.empty:
    charts[1].info("Add weekly study hours to see the study-time chart.")
else:
    study_courses = sorted(study_data["Course"].tolist())
    if "study_courses" not in st.session_state:
        st.session_state["study_courses"] = study_courses
    else:
        st.session_state["study_courses"] = [
            name for name in st.session_state["study_courses"] if name in study_courses
        ]
    selected_study_courses = st.multiselect(
        "Courses for study-time chart",
        study_courses,
        key="study_courses",
    )
    if selected_study_courses:
        selected_study = study_data.loc[
            study_data["Course"].isin(selected_study_courses)
        ]
        mean, median = st.columns(2)
        mean.metric("Mean weekly study hours", f"{selected_study['Weekly Study Hours'].mean():.1f}")
        median.metric(
            "Median weekly study hours",
            f"{selected_study['Weekly Study Hours'].median():.1f}",
        )
        charts[1].altair_chart(
            bar_chart(
                selected_study.rename(columns={"Weekly Study Hours": "Hours"}),
                "Hours",
                "Weekly study hours by course",
                "Hours per week",
            )
        )
    else:
        charts[1].info("Select a course to show the study-time chart.")
