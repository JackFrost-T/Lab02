import streamlit as st


st.set_page_config(
    page_title="Course & Credit Planner",
    page_icon=":material/school:",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def show_homepage():
    st.title("Welcome to the Data Dashboard! 📊")
    st.write("This application collects survey data and visualizes it in charts.")

    st.header("How to use this app")
    st.write(
        "- **Survey page:** Submit a category and value. For course planning, "
        "add a course name, credits, and estimated weekly study hours. Responses "
        "are saved in `data.csv` and shown in the survey table.\n"
        "- **Visuals page:** Explore the semester data from `data.json` and view "
        "visual summaries of survey responses from `data.csv`."
    )
    st.write(
        "This project is part of CS 1301's Lab 2."
    )

overview_page = st.Page(
    show_homepage,
    title="Overview",
    icon=":material/home:",
    default=True,
    url_path="",
)
visuals_page = st.Page(
    "pages/Visuals.py",
    title="Visuals",
    icon=":material/analytics:",
)
survey_page = st.Page(
    "pages/Survey.py",
    title="Add a course",
    icon=":material/edit_note:",
)
page = st.navigation(
    [overview_page, visuals_page, survey_page],
    position="hidden",
)

with st.container(horizontal=True, horizontal_alignment="left"):
    st.page_link(overview_page, label="Overview", icon=":material/home:")
    st.page_link(visuals_page, label="Visuals", icon=":material/analytics:")
    st.page_link(survey_page, label="Add a course", icon=":material/edit_note:")

page.run()
