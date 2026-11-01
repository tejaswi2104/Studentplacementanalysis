
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="PlacementIQ",
    page_icon="🎓",
    layout="wide"
)

# ---------------- SAMPLE DATA ----------------
def create_data():
    rng = np.random.default_rng(42)

    departments = ["CSE", "ECE", "EEE", "MECH", "CIVIL"]
    skills_list = [
        "Java", "Python", "SQL", "DSA",
        "Web Development", "Machine Learning",
        "Communication", "C++"
    ]

    students = []

    for i in range(1, 101):
        eligible = i % 10 != 0
        placed = eligible and i % 3 != 0

        students.append({
            "student_id": i,
            "roll_no": f"TEST{i:03}",
            "student_name": f"Test Student {i}",
            "department": departments[(i - 1) % 5],
            "graduation_year": 2026,
            "eligible": eligible,
            "placement_status": "Placed" if placed else "Not Placed"
        })

    students_df = pd.DataFrame(students)

    placements = []
    companies = ["Example Tech A", "Example Tech B", "Example Analytics C"]
    roles = ["Software Developer", "Analyst", "Junior Engineer"]

    for _, student in students_df.iterrows():
        if student["placement_status"] == "Placed":
            placements.append({
                "student_id": student["student_id"],
                "roll_no": student["roll_no"],
                "student_name": student["student_name"],
                "department": student["department"],
                "company": rng.choice(companies),
                "role": rng.choice(roles),
                "package_lpa": round(float(rng.uniform(3, 12)), 2),
                "placement_year": 2026
            })

    placements_df = pd.DataFrame(placements)

    student_skills = []

    for student_id in students_df["student_id"]:
        selected = rng.choice(skills_list, size=3, replace=False)

        for skill in selected:
            student_skills.append({
                "student_id": student_id,
                "skill_name": skill
            })

    skills_df = pd.DataFrame(student_skills)

    return students_df, placements_df, skills_df


if "students" not in st.session_state:
    students, placements, skills = create_data()
    st.session_state.students = students
    st.session_state.placements = placements
    st.session_state.skills = skills

students = st.session_state.students
placements = st.session_state.placements
skills = st.session_state.skills

# ---------------- CUSTOM STYLE ----------------

st.markdown("""
<style>
/* Main background */
.stApp,
[data-testid="stAppViewContainer"] {
    background-color: #f5f7fb;
}

/* Main text */
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] span,
[data-testid="stAppViewContainer"] li {
    color: #1f2937 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #14213d;
}

[data-testid="stSidebar"] {
    background-color: #14213d !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] div {
    color: white !important;
}

[data-testid="stSidebar"] input {
    color: #14213d !important;
    background-color: white !important;
}

/* Input fields */
.stTextInput input,
.stNumberInput input {
    background-color: white !important;
    color: #1f2937 !important;
}

/* Buttons */
.stButton button {
    background-color: #2563eb;
    color: white !important;
    border-radius: 8px;
}

/* Metrics */
[data-testid="stMetricValue"] {
    color: #14213d !important;
}

/* Add, Save and Download buttons */
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    background-color: #2563eb !important;
    color: white !important;
    border: 1px solid #2563eb !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* Button hover */
.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
    background-color: #1d4ed8 !important;
    color: white !important;
}
</style>

""", unsafe_allow_html=True)
# ---------------- SIDEBAR ----------------
st.sidebar.title("🎓 PlacementIQ")
st.sidebar.caption("Student Placement Data Analysis")

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Students",
        "Placements",
        "Department Analysis",
        "Package Analytics",
        "Skill Demand",
        "Data Import",
        "Reports"
    ]
)

st.sidebar.divider()
st.sidebar.info("Demo application using fictional sample records.")

# ---------------- HEADER ----------------
st.title("🎓 PlacementIQ")
st.write("Student Placement Data Analysis System")
st.divider()

# Refresh references after session-state changes
students = st.session_state.students
placements = st.session_state.placements
skills = st.session_state.skills

eligible_students = students[students["eligible"] == True]
placed_students = students[
    (students["eligible"] == True) &
    (students["placement_status"] == "Placed")
]

total_students = len(students)
total_eligible = len(eligible_students)
total_placed = len(placed_students)

placement_rate = (
    total_placed / total_eligible * 100
    if total_eligible > 0 else 0
)

# ---------------- OVERVIEW ----------------
if page == "Overview":

    st.subheader("Placement Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Students", total_students)
    c2.metric("Eligible Students", total_eligible)
    c3.metric("Students Placed", total_placed)
    c4.metric("Placement Rate", f"{placement_rate:.1f}%")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Placement Status")

        status_data = students["placement_status"].value_counts().reset_index()
        status_data.columns = ["Status", "Count"]

        fig = px.pie(
            status_data,
            names="Status",
            values="Count",
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Department-wise Students")

        dept_data = students.groupby("department").size().reset_index(name="Students")

        fig = px.bar(
            dept_data,
            x="department",
            y="Students",
            color="department"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent Placement Records")
    st.dataframe(placements.tail(10), use_container_width=True)

    st.caption(
        "Placement rate = Eligible students placed / Total eligible students × 100"
    )

# ---------------- STUDENTS ----------------
elif page == "Students":

    st.subheader("Student Management")

    with st.expander("➕ Add New Student"):
        with st.form("student_form"):
            roll_no = st.text_input("Roll Number")
            name = st.text_input("Student Name")
            department = st.selectbox(
                "Department",
                ["CSE", "ECE", "EEE", "MECH", "CIVIL"]
            )
            year = st.number_input(
                "Graduation Year",
                min_value=2026,
                max_value=2035,
                value=2029
            )
            eligible = st.checkbox("Eligible for placement", value=True)

            submitted = st.form_submit_button("Add Student")

            if submitted:
                if not roll_no.strip() or not name.strip():
                    st.error("Please enter both roll number and name.")
                elif roll_no in st.session_state.students["roll_no"].values:
                    st.error("This roll number already exists.")
                else:
                    new_id = int(st.session_state.students["student_id"].max()) + 1

                    new_student = pd.DataFrame([{
                        "student_id": new_id,
                        "roll_no": roll_no.strip(),
                        "student_name": name.strip(),
                        "department": department,
                        "graduation_year": int(year),
                        "eligible": eligible,
                        "placement_status": "Not Placed"
                    }])

                    st.session_state.students = pd.concat(
                        [st.session_state.students, new_student],
                        ignore_index=True
                    )

                    st.success("Student added successfully!")
                    st.rerun()

    st.divider()

    search = st.text_input("Search by name or roll number")

    filtered = st.session_state.students.copy()

    if search:
        filtered = filtered[
            filtered["student_name"].str.contains(search, case=False, na=False) |
            filtered["roll_no"].str.contains(search, case=False, na=False)
        ]

    st.dataframe(filtered, use_container_width=True)

    st.download_button(
        "Download Student Data",
        filtered.to_csv(index=False),
        "students.csv",
        "text/csv"
    )

# ---------------- PLACEMENTS ----------------
elif page == "Placements":

    st.subheader("Placement Management")

    available = st.session_state.students[
        (st.session_state.students["eligible"] == True) &
        (~st.session_state.students["student_id"].isin(
            st.session_state.placements["student_id"]
        ))
    ]

    if len(available) > 0:
        with st.expander("➕ Add Placement Record"):
            with st.form("placement_form"):
                student_id = st.selectbox(
                    "Select Student",
                    available["student_id"].tolist(),
                    format_func=lambda x: (
                        available.loc[
                            available["student_id"] == x, "student_name"
                        ].iloc[0]
                        + " (" +
                        available.loc[
                            available["student_id"] == x, "roll_no"
                        ].iloc[0] + ")"
                    )
                )

                company = st.text_input("Company Name")
                role = st.text_input("Job Role")
                package = st.number_input(
                    "Package (LPA)",
                    min_value=0.1,
                    max_value=100.0,
                    value=5.0
                )
                year = st.number_input(
                    "Placement Year",
                    min_value=2026,
                    max_value=2035,
                    value=2026
                )

                submitted = st.form_submit_button("Save Placement")

                if submitted:
                    if not company.strip() or not role.strip():
                        st.error("Enter company and job role.")
                    else:
                        student = st.session_state.students[
                            st.session_state.students["student_id"] == student_id
                        ].iloc[0]

                        new_placement = pd.DataFrame([{
                            "student_id": student_id,
                            "roll_no": student["roll_no"],
                            "student_name": student["student_name"],
                            "department": student["department"],
                            "company": company.strip(),
                            "role": role.strip(),
                            "package_lpa": package,
                            "placement_year": int(year)
                        }])

                        st.session_state.placements = pd.concat(
                            [st.session_state.placements, new_placement],
                            ignore_index=True
                        )

                        st.session_state.students.loc[
                            st.session_state.students["student_id"] == student_id,
                            "placement_status"
                        ] = "Placed"

                        st.success("Placement record added!")
                        st.rerun()
    else:
        st.info("No eligible, unplaced students are currently available.")

    st.divider()
    st.dataframe(st.session_state.placements, use_container_width=True)

    st.download_button(
        "Download Placement Data",
        st.session_state.placements.to_csv(index=False),
        "placements.csv",
        "text/csv"
    )

# ---------------- DEPARTMENT ANALYSIS ----------------
elif page == "Department Analysis":

    st.subheader("Department-wise Placement Analysis")

    department_data = st.session_state.students.groupby("department").agg(
        total_students=("student_id", "count"),
        eligible_students=("eligible", "sum")
    ).reset_index()

    placed_data = (
        st.session_state.students[
            (st.session_state.students["eligible"] == True) &
            (st.session_state.students["placement_status"] == "Placed")
        ]
        .groupby("department")
        .size()
        .reset_index(name="placed_students")
    )

    department_data = department_data.merge(
        placed_data, on="department", how="left"
    )

    department_data["placed_students"] = (
        department_data["placed_students"].fillna(0)
    )

    department_data["placement_rate"] = (
        department_data["placed_students"] /
        department_data["eligible_students"].replace(0, np.nan) * 100
    ).fillna(0)

    st.dataframe(department_data, use_container_width=True)

    fig = px.bar(
        department_data,
        x="department",
        y="placement_rate",
        color="department",
        title="Department-wise Placement Rate (%)"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------- PACKAGE ANALYTICS ----------------
elif page == "Package Analytics":

    st.subheader("Package Distribution Analysis")

    data = st.session_state.placements

    if len(data) > 0:
        c1, c2, c3 = st.columns(3)

        c1.metric("Average Package", f"{data['package_lpa'].mean():.2f} LPA")
        c2.metric("Median Package", f"{data['package_lpa'].median():.2f} LPA")
        c3.metric("Highest Package", f"{data['package_lpa'].max():.2f} LPA")

        fig = px.histogram(
            data,
            x="package_lpa",
            nbins=10,
            title="Package Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

        company_data = data.groupby("company")["package_lpa"].mean().reset_index()

        fig = px.bar(
            company_data,
            x="company",
            y="package_lpa",
            title="Average Package by Company"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No placement records available.")

# ---------------- SKILL DEMAND ----------------
elif page == "Skill Demand":

    st.subheader("Student Skill Analysis")

    st.caption(
        "This page measures skills listed in student profiles, "
        "not verified employer demand."
    )

    skill_counts = (
        st.session_state.skills["skill_name"]
        .value_counts()
        .reset_index()
    )

    skill_counts.columns = ["Skill", "Student Count"]

    fig = px.bar(
        skill_counts,
        x="Skill",
        y="Student Count",
        color="Skill",
        title="Skills Across Student Profiles"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(skill_counts, use_container_width=True)

    with st.expander("➕ Add a Skill to a Student"):
        student_options = st.session_state.students["student_id"].tolist()

        with st.form("skill_form"):
            selected_student = st.selectbox(
                "Student ID",
                student_options
            )

            skill_name = st.text_input("Skill Name")
            submitted = st.form_submit_button("Add Skill")

            if submitted:
                if not skill_name.strip():
                    st.error("Enter a skill name.")
                elif (
                    (st.session_state.skills["student_id"] == selected_student) &
                    (st.session_state.skills["skill_name"].str.lower() == skill_name.strip().lower())
                ).any():
                    st.warning("This student already has this skill.")
                else:
                    new_skill = pd.DataFrame([{
                        "student_id": selected_student,
                        "skill_name": skill_name.strip()
                    }])

                    st.session_state.skills = pd.concat(
                        [st.session_state.skills, new_skill],
                        ignore_index=True
                    )

                    st.success("Skill added!")
                    st.rerun()

# ---------------- DATA IMPORT ----------------
elif page == "Data Import":

    st.subheader("Import Student CSV")

    st.write("Upload a CSV file to preview its contents.")

    uploaded_file = st.file_uploader(
        "Choose student CSV file",
        type=["csv"]
    )

    if uploaded_file is not None:
        try:
            imported_data = pd.read_csv(uploaded_file)

            st.success("CSV uploaded successfully!")
            st.write("Preview:")
            st.dataframe(imported_data, use_container_width=True)

            st.info(
                "This is a preview only. The uploaded CSV is not permanently "
                "stored in the application."
            )

        except Exception as e:
            st.error(f"Unable to read CSV: {e}")

# ---------------- REPORTS ----------------
elif page == "Reports":

    st.subheader("Placement Reports")

    st.write("Download reports generated from the current application data.")

    st.download_button(
        "Download Students Report",
        st.session_state.students.to_csv(index=False),
        "students_report.csv",
        "text/csv"
    )

    st.download_button(
        "Download Placements Report",
        st.session_state.placements.to_csv(index=False),
        "placements_report.csv",
        "text/csv"
    )

    st.download_button(
        "Download Skills Report",
        st.session_state.skills.to_csv(index=False),
        "skills_report.csv",
        "text/csv"
    )

    st.write("### Overall Summary")

    summary = pd.DataFrame({
        "Metric": [
            "Total Students",
            "Eligible Students",
            "Placed Students",
            "Placement Rate (%)"
        ],
        "Value": [
            len(st.session_state.students),
            int(st.session_state.students["eligible"].sum()),
            len(st.session_state.placements),
            round(placement_rate, 2)
        ]
    })

    st.dataframe(summary, use_container_width=True)

# ---------------- FOOTER ----------------
st.divider()
st.caption(
    "PlacementIQ | Student Placement Data Analysis System | "
    "Academic Demonstration Project | Fictional Sample Data"
)
