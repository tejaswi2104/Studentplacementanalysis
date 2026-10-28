
import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector
from mysql.connector import Error

st.set_page_config(
    page_title="PlacementIQ | Analytics Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# STYLING
# =====================================================
st.markdown("""
<style>
.stApp {
    background-color: #f5f7fb;
    color: #1f2937;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    color: #1e3a8a !important;
    font-weight: 700;
}
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li,
.stApp [data-testid="stWidgetLabel"] p,
.stApp label {
    color: #1f2937;
}
[data-testid="stSidebar"] {
    background-color: #111827;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #ffffff !important;
}
.stApp input, .stApp textarea {
    color: #111827 !important;
    background-color: #ffffff !important;
}
.stApp [data-baseweb="select"] > div {
    background-color: #ffffff !important;
}
.stApp [data-baseweb="select"] span {
    color: #111827 !important;
}
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e2e8f0;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(15,23,42,.05);
}
[data-testid="stMetricLabel"],
[data-testid="stMetricValue"],
[data-testid="stMetricDelta"] {
    color: #111827 !important;
}
.stApp button, .stApp button p,
.stApp button span, .stApp button div {
    color: white !important;
}
.stApp div.stButton > button,
.stApp div.stFormSubmitButton > button,
.stApp button[kind="primary"],
.stApp button[kind="secondary"] {
    background-color: #2563eb !important;
    color: white !important;
    border: 1px solid #1d4ed8 !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    padding: 10px 18px !important;
}
.stApp div.stButton > button:hover,
.stApp div.stFormSubmitButton > button:hover {
    background-color: #1d4ed8 !important;
}
div[data-testid="stPlotlyChart"] {
    background: white;
    border-radius: 12px;
    padding: 8px;
    border: 1px solid #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
st.title("🎓 PlacementIQ")
st.markdown(
    "**STUDENT PLACEMENT DATA ANALYSIS SYSTEM**  \n"
    "Analyze placement outcomes, package trends, departments and skills."
)
st.divider()

# =====================================================
# DEMO DATA
# =====================================================
def initialize_demo_data():
    if "demo_students" not in st.session_state:
        st.session_state.demo_students = pd.DataFrame([
            [1, "MBU001", "Aarav Kumar", "CSE", 2029, 1, "Placed"],
            [2, "MBU002", "Priya Sharma", "CSE", 2029, 1, "Placed"],
            [3, "MBU003", "Rahul Reddy", "ECE", 2029, 1, "Not Placed"],
            [4, "MBU004", "Sneha Rao", "IT", 2029, 1, "Placed"],
            [5, "MBU005", "Arjun Verma", "CSE", 2029, 1, "Not Placed"],
            [6, "MBU006", "Kavya Devi", "ECE", 2029, 1, "Placed"],
            [7, "MBU007", "Vikram Singh", "EEE", 2029, 0, "Not Placed"],
            [8, "MBU008", "Ananya Reddy", "IT", 2029, 1, "Placed"],
            [9, "MBU009", "Manoj Kumar", "MECH", 2029, 1, "Not Placed"],
            [10, "MBU010", "Divya Sri", "CSE", 2029, 1, "Placed"],
        ], columns=[
            "student_id", "roll_no", "student_name", "department",
            "graduation_year", "eligible", "placement_status"
        ])

    if "demo_placements" not in st.session_state:
        st.session_state.demo_placements = pd.DataFrame([
            [1, 1, "Google", "Software Engineer", 18.0, 2026],
            [2, 2, "Microsoft", "Software Engineer", 16.0, 2026],
            [3, 4, "Amazon", "Graduate Engineer", 12.0, 2026],
            [4, 6, "Deloitte", "Analyst", 7.0, 2026],
            [5, 8, "IBM", "Associate Developer", 8.0, 2026],
            [6, 10, "Infosys", "Systems Engineer", 5.0, 2026],
        ], columns=[
            "placement_id", "student_id", "company", "role",
            "package_lpa", "placement_year"
        ])

    if "demo_skills" not in st.session_state:
        st.session_state.demo_skills = pd.DataFrame([
            [1, "Java"], [2, "SQL"], [3, "Python"],
            [4, "DSA"], [5, "Communication"]
        ], columns=["skill_id", "skill_name"])

    if "demo_student_skills" not in st.session_state:
        st.session_state.demo_student_skills = pd.DataFrame([
            [1, 1], [1, 2], [1, 4],
            [2, 1], [2, 4], [2, 5],
            [3, 2], [3, 3], [4, 1],
            [4, 2], [5, 4], [6, 1],
            [7, 3], [8, 1], [8, 5],
            [9, 2], [10, 1], [10, 4]
        ], columns=["student_id", "skill_id"])

initialize_demo_data()

# =====================================================
# DATABASE CONNECTION
# =====================================================
st.sidebar.title("🎓 PlacementIQ")
st.sidebar.caption("Student Placement Analytics")
st.sidebar.divider()
st.sidebar.subheader("Database Connection")

# Add these values in Streamlit Cloud Secrets when a hosted
# MySQL database is available. Never use localhost for cloud MySQL.
conn = None
db_error = None

try:
    if "mysql" in st.secrets:
        cfg = st.secrets["mysql"]
        conn = mysql.connector.connect(
            host=cfg["host"],
            port=int(cfg.get("port", 3306)),
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            connection_timeout=5
        )
        st.sidebar.success("Hosted MySQL connected")
    else:
        st.sidebar.info("Demo mode: sample data")
except Exception as e:
    db_error = str(e)
    conn = None
    st.sidebar.warning("Demo mode: database unavailable")

if conn is None:
    st.caption(
        "Demo mode is active. The displayed sample data is illustrative. "
        "Changes made in this mode are temporary and are not saved to MySQL."
    )

# =====================================================
# DATA ACCESS
# =====================================================
def read_data(query, params=None):
    if conn is None:
        return pd.DataFrame()

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        return pd.DataFrame(cursor.fetchall())
    finally:
        cursor.close()


def run_query(query, values=()):
    if conn is None:
        raise RuntimeError(
            "Database editing requires a configured hosted MySQL database."
        )

    cursor = conn.cursor()
    try:
        cursor.execute(query, values)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


def get_students():
    if conn is None:
        return st.session_state.demo_students.copy()

    return read_data("""
        SELECT student_id, roll_no, student_name, department,
               graduation_year, eligible, placement_status
        FROM students
        ORDER BY student_id
    """)


def get_placements():
    if conn is None:
        students = get_students()
        p = st.session_state.demo_placements.copy()
        return p.merge(
            students[["student_id", "roll_no", "student_name", "department"]],
            on="student_id",
            how="left"
        )[[
            "placement_id", "student_id", "roll_no", "student_name",
            "department", "company", "role", "package_lpa", "placement_year"
        ]]

    return read_data("""
        SELECT p.placement_id, s.student_id, s.roll_no,
               s.student_name, s.department, p.company, p.role,
               p.package_lpa, p.placement_year
        FROM placements p
        JOIN students s ON p.student_id = s.student_id
        ORDER BY p.placement_year DESC, p.placement_id DESC
    """)


def get_skills():
    if conn is None:
        return st.session_state.demo_skills.copy()

    return read_data("""
        SELECT skill_id, skill_name FROM skills ORDER BY skill_name
    """)


def get_skill_demand():
    if conn is None:
        skills = get_skills()
        mappings = st.session_state.demo_student_skills
        counts = mappings.groupby("skill_id")["student_id"].nunique()
        skills["students_with_skill"] = (
            skills["skill_id"].map(counts).fillna(0).astype(int)
        )
        return skills[["skill_name", "students_with_skill"]].sort_values(
            "students_with_skill", ascending=False
        )

    return read_data("""
        SELECT sk.skill_name,
               COUNT(DISTINCT ss.student_id) AS students_with_skill
        FROM skills sk
        LEFT JOIN student_skills ss ON sk.skill_id = ss.skill_id
        GROUP BY sk.skill_id, sk.skill_name
        ORDER BY students_with_skill DESC, sk.skill_name
    """)


def save_student(roll, name, department, year, eligible):
    if conn is not None:
        run_query("""
            INSERT INTO students
            (roll_no, student_name, department, graduation_year,
             eligible, placement_status)
            VALUES (%s, %s, %s, %s, %s, 'Not Placed')
        """, (roll, name, department, year, int(eligible)))
        return

    students = get_students()
    if students["roll_no"].astype(str).str.lower().eq(roll.lower()).any():
        raise ValueError("That roll number already exists.")

    new_id = int(students["student_id"].max()) + 1 if not students.empty else 1
    new_row = pd.DataFrame([[
        new_id, roll, name, department, year, int(eligible), "Not Placed"
    ]], columns=students.columns)
    st.session_state.demo_students = pd.concat(
        [students, new_row], ignore_index=True
    )


def save_placement(sid, company, role, package, year):
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO placements
                (student_id, company, role, package_lpa, placement_year)
                VALUES (%s, %s, %s, %s, %s)
            """, (sid, company, role, package, year))
            cursor.execute("""
                UPDATE students SET placement_status='Placed'
                WHERE student_id=%s
            """, (sid,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
        return

    p = st.session_state.demo_placements.copy()
    if (not p.empty) and (p["student_id"] == sid).any():
        raise ValueError("This student already has a placement record.")

    new_id = int(p["placement_id"].max()) + 1 if not p.empty else 1
    st.session_state.demo_placements = pd.concat([
        p,
        pd.DataFrame([[
            new_id, sid, company, role, package, year
        ]], columns=p.columns)
    ], ignore_index=True)

    students = get_students()
    students.loc[students["student_id"] == sid, "placement_status"] = "Placed"
    st.session_state.demo_students = students


def save_skill(skill_name):
    if conn is not None:
        run_query(
            "INSERT INTO skills (skill_name) VALUES (%s)",
            (skill_name,)
        )
        return

    skills = get_skills()
    if skills["skill_name"].str.lower().eq(skill_name.lower()).any():
        raise ValueError("That skill already exists.")

    new_id = int(skills["skill_id"].max()) + 1 if not skills.empty else 1
    st.session_state.demo_skills = pd.concat([
        skills,
        pd.DataFrame([[new_id, skill_name]], columns=skills.columns)
    ], ignore_index=True)


def assign_skill(sid, kid):
    if conn is not None:
        run_query("""
            INSERT INTO student_skills (student_id, skill_id)
            VALUES (%s, %s)
        """, (sid, kid))
        return

    mappings = st.session_state.demo_student_skills.copy()
    duplicate = (
        (mappings["student_id"] == sid) &
        (mappings["skill_id"] == kid)
    ).any()
    if duplicate:
        raise ValueError("This student already has that skill.")

    st.session_state.demo_student_skills = pd.concat([
        mappings,
        pd.DataFrame([[sid, kid]], columns=mappings.columns)
    ], ignore_index=True)


# =====================================================
# NAVIGATION
# =====================================================
page = st.sidebar.radio(
    "📌 Navigation",
    [
        "Overview", "Students", "Placements",
        "Department Analysis", "Package Analytics",
        "Skill Demand", "Data Import", "Reports"
    ]
)

# =====================================================
# LOAD DATA AND METRICS
# =====================================================
try:
    students = get_students()
    placements = get_placements()
except Exception as e:
    st.error(f"Could not load records: {e}")
    st.stop()

eligible_count = (
    int(pd.to_numeric(students["eligible"], errors="coerce").fillna(0).sum())
    if not students.empty else 0
)

eligible_ids = set(
    students.loc[
        pd.to_numeric(students["eligible"], errors="coerce").fillna(0) == 1,
        "student_id"
    ].astype(int)
) if not students.empty else set()

placed_ids = set(
    placements["student_id"].dropna().astype(int)
) if not placements.empty else set()

eligible_placed_count = len(eligible_ids & placed_ids)
placement_rate = (
    eligible_placed_count / eligible_count * 100 if eligible_count else 0
)

# =====================================================
# OVERVIEW
# =====================================================
if page == "Overview":
    st.subheader("📊 Placement Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Students", len(students))
    c2.metric("Eligible Students", eligible_count)
    c3.metric("Eligible Students Placed", eligible_placed_count)
    c4.metric("Placement Rate", f"{placement_rate:.1f}%")

    st.caption(
        "Placement Rate = eligible students with placement records "
        "÷ total eligible students × 100."
    )

    if not students.empty:
        dept = students.groupby("department").agg(
            Total_Students=("student_id", "count"),
            Eligible_Students=("eligible", "sum")
        ).reset_index()

        if not placements.empty:
            valid = placements[
                placements["student_id"].astype(int).isin(eligible_ids)
            ]
            placed_dept = valid.groupby("department").size().reset_index(
                name="Placed_Students"
            )
        else:
            placed_dept = pd.DataFrame(
                columns=["department", "Placed_Students"]
            )

        dept = dept.merge(placed_dept, on="department", how="left")
        dept["Placed_Students"] = dept["Placed_Students"].fillna(0).astype(int)
        dept["Placement_Rate"] = (
            dept["Placed_Students"] /
            dept["Eligible_Students"].replace(0, float("nan")) * 100
        ).fillna(0).round(2)

        left, right = st.columns(2)
        with left:
            st.plotly_chart(px.bar(
                dept, x="department", y="Total_Students",
                color="department", title="Students by Department"
            ), use_container_width=True)
        with right:
            st.plotly_chart(px.bar(
                dept, x="department", y="Placement_Rate",
                color="department", title="Placement Rate by Department",
                labels={"Placement_Rate": "Placement Rate (%)"}
            ), use_container_width=True)

    st.subheader("🕒 Recent Placements")
    st.dataframe(placements.head(10), use_container_width=True, hide_index=True)

# =====================================================
# STUDENTS
# =====================================================
elif page == "Students":
    st.subheader("👨‍🎓 Student Management")

    with st.expander("➕ Add a Student", expanded=True):
        with st.form("student_form"):
            roll = st.text_input("Roll Number")
            name = st.text_input("Student Name")
            dept_choice = st.selectbox(
                "Department", ["CSE", "ECE", "EEE", "IT", "MECH", "CIVIL", "Other"]
            )
            department = (
                st.text_input("Enter Department Name")
                if dept_choice == "Other" else dept_choice
            )
            graduation_year = st.number_input(
                "Graduation Year", min_value=2026, max_value=2040, value=2029
            )
            eligible = st.checkbox("Eligible for placements", value=True)
            submitted = st.form_submit_button(
                "Save Student", type="primary", use_container_width=True
            )

            if submitted:
                if not roll.strip() or not name.strip() or not department.strip():
                    st.error("Please fill in all required fields.")
                else:
                    try:
                        save_student(
                            roll.strip(), name.strip(), department.strip(),
                            int(graduation_year), eligible
                        )
                        st.success("Student added.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not add student: {e}")

    st.subheader("📋 Student Records")
    search = st.text_input("Search by roll number, name or department")
    filtered = students
    if search.strip():
        mask = students.astype(str).apply(
            lambda col: col.str.contains(
                search.strip(), case=False, na=False, regex=False
            )
        ).any(axis=1)
        filtered = students[mask]

    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Download Student CSV",
        filtered.to_csv(index=False).encode("utf-8"),
        "students.csv", "text/csv"
    )

# =====================================================
# PLACEMENTS
# =====================================================
elif page == "Placements":
    st.subheader("💼 Placement Management")

    already_placed = set(
        placements["student_id"].dropna().astype(int)
    ) if not placements.empty else set()

    available = students[
        (pd.to_numeric(students["eligible"], errors="coerce").fillna(0) == 1) &
        (~students["student_id"].astype(int).isin(already_placed))
    ]

    if available.empty:
        st.info("No eligible unplaced students are available.")
    else:
        with st.form("placement_form"):
            student_map = {
                f"{r.roll_no} — {r.student_name} ({r.department})":
                int(r.student_id)
                for r in available.itertuples()
            }
            selected = st.selectbox("Select Student", list(student_map.keys()))
            company = st.text_input("Company Name")
            role = st.text_input("Job Role")
            package = st.number_input(
                "Package (LPA)", min_value=0.01, max_value=1000.0,
                value=6.0, step=0.5
            )
            year = st.number_input(
                "Placement Year", min_value=2020, max_value=2040, value=2026
            )
            submitted = st.form_submit_button(
                "Save Placement", type="primary", use_container_width=True
            )

            if submitted:
                if not company.strip() or not role.strip():
                    st.error("Enter the company name and job role.")
                else:
                    try:
                        save_placement(
                            student_map[selected], company.strip(),
                            role.strip(), float(package), int(year)
                        )
                        st.success("Placement saved.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not save placement: {e}")

    st.subheader("📋 Placement Records")
    st.dataframe(placements, use_container_width=True, hide_index=True)

# =====================================================
# DEPARTMENT ANALYSIS
# =====================================================
elif page == "Department Analysis":
    st.subheader("🏢 Department-wise Analysis")

    if students.empty:
        st.info("Add student records to view analysis.")
    else:
        dept = students.groupby("department").agg(
            Total_Students=("student_id", "count"),
            Eligible_Students=("eligible", "sum")
        ).reset_index()

        valid = placements[
            placements["student_id"].astype(int).isin(eligible_ids)
        ] if not placements.empty else pd.DataFrame()

        placed = (
            valid.groupby("department").size().reset_index(
                name="Placed_Students"
            ) if not valid.empty else
            pd.DataFrame(columns=["department", "Placed_Students"])
        )

        dept = dept.merge(placed, on="department", how="left")
        dept["Placed_Students"] = dept["Placed_Students"].fillna(0).astype(int)
        dept["Placement_Rate_%"] = (
            dept["Placed_Students"] /
            dept["Eligible_Students"].replace(0, float("nan")) * 100
        ).fillna(0).round(2)

        st.dataframe(dept, use_container_width=True, hide_index=True)
        st.plotly_chart(px.bar(
            dept, x="department", y="Placement_Rate_%",
            color="department", title="Placement Rate by Department"
        ), use_container_width=True)

        comparison = dept.melt(
            id_vars="department",
            value_vars=["Eligible_Students", "Placed_Students"],
            var_name="Student Category",
            value_name="Number of Students"
        )
        st.plotly_chart(px.bar(
            comparison, x="department", y="Number of Students",
            color="Student Category", barmode="group",
            title="Eligible vs Placed Students"
        ), use_container_width=True)

# =====================================================
# PACKAGE ANALYTICS
# =====================================================
elif page == "Package Analytics":
    st.subheader("💰 Package Analytics")

    if placements.empty:
        st.info("Record placements to view package analytics.")
    else:
        packages = pd.to_numeric(
            placements["package_lpa"], errors="coerce"
        ).dropna()

        if packages.empty:
            st.info("No valid package values available.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Average Package", f"{packages.mean():.2f} LPA")
            c2.metric("Median Package", f"{packages.median():.2f} LPA")
            c3.metric("Highest Package", f"{packages.max():.2f} LPA")

            st.plotly_chart(px.histogram(
                placements, x="package_lpa", nbins=10,
                title="Package Distribution",
                labels={"package_lpa": "Package (LPA)"}
            ), use_container_width=True)

            company_summary = placements.groupby("company").agg(
                Average_Package=("package_lpa", "mean"),
                Highest_Package=("package_lpa", "max"),
                Students_Placed=("student_id", "nunique")
            ).reset_index().round(2)

            st.plotly_chart(px.bar(
                company_summary, x="company", y="Average_Package",
                title="Average Package by Company",
                hover_data=["Highest_Package", "Students_Placed"]
            ), use_container_width=True)

            st.subheader("Package Statistics")
            stats = pd.DataFrame({
                "Metric": ["Mean", "Median", "Minimum", "Maximum"],
                "Package (LPA)": [
                    packages.mean(), packages.median(),
                    packages.min(), packages.max()
                ]
            }).round(2)
            st.dataframe(stats, use_container_width=True, hide_index=True)

# =====================================================
# SKILL DEMAND
# =====================================================
elif page == "Skill Demand":
    st.subheader("🧠 Skill Management and Demand")

    with st.form("skill_form"):
        skill_name = st.text_input("Skill Name (e.g. Java, SQL, Python)")
        skill_submit = st.form_submit_button("Save Skill", type="primary")

        if skill_submit:
            if skill_name.strip():
                try:
                    save_skill(skill_name.strip())
                    st.success("Skill added.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not add skill: {e}")
            else:
                st.error("Enter a skill name.")

    skills = get_skills()
    students = get_students()

    if not students.empty and not skills.empty:
        with st.form("student_skill_form"):
            student_map = {
                f"{r.roll_no} — {r.student_name}": int(r.student_id)
                for r in students.itertuples()
            }
            selected_student = st.selectbox(
                "Select Student", list(student_map.keys())
            )
            skill_map = dict(zip(skills["skill_name"], skills["skill_id"]))
            selected_skill = st.selectbox(
                "Select Skill", list(skill_map.keys())
            )
            assign_submit = st.form_submit_button(
                "Assign Skill", type="primary"
            )

            if assign_submit:
                try:
                    assign_skill(
                        student_map[selected_student],
                        int(skill_map[selected_skill])
                    )
                    st.success("Skill assigned.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not assign skill: {e}")

    st.subheader("📈 Skills Report")
    st.caption(
        "This chart counts skills reported by students; "
        "it does not independently measure employer demand."
    )
    demand = get_skill_demand()
    st.dataframe(demand, use_container_width=True, hide_index=True)

    if not demand.empty:
        st.plotly_chart(px.bar(
            demand, x="skill_name", y="students_with_skill",
            title="Skills Reported by Students"
        ), use_container_width=True)

# =====================================================
# DATA IMPORT
# =====================================================
elif page == "Data Import":
    st.subheader("📂 Bulk CSV Data Import")
    st.info(
        "Upload approved or synthetic data. Back up your database before "
        "bulk importing. Demo-mode changes are temporary."
    )

    st.markdown("""
**Required CSV columns**

- Students: `roll_no, student_name, department, graduation_year, eligible, placement_status`
- Placements: `roll_no, company, role, package_lpa, placement_year`
- Skills: `skill_name`
""")

    student_file = st.file_uploader(
        "Students CSV", type=["csv"], key="students_csv"
    )
    placement_file = st.file_uploader(
        "Placements CSV", type=["csv"], key="placements_csv"
    )
    skill_file = st.file_uploader(
        "Skills CSV", type=["csv"], key="skills_csv"
    )

    if st.button("Import Selected Files", type="primary"):
        try:
            imported_any = False

            if student_file is not None:
                df = pd.read_csv(student_file, dtype={"roll_no": str})
                required = {
                    "roll_no", "student_name", "department",
                    "graduation_year", "eligible", "placement_status"
                }
                if not required.issubset(df.columns):
                    raise ValueError(
                        "Students CSV is missing required columns."
                    )
                if conn is not None:
                    for _, r in df.iterrows():
                        eligible_text = str(r["eligible"]).strip().lower()
                        if eligible_text not in (
                            "0", "1", "true", "false", "yes", "no"
                        ):
                            raise ValueError("Invalid eligibility value.")
                        save_student(
                            str(r["roll_no"]).strip(),
                            str(r["student_name"]).strip(),
                            str(r["department"]).strip(),
                            int(r["graduation_year"]),
                            eligible_text in ("1", "true", "yes")
                        )
                else:
                    current = get_students()
                    for _, r in df.iterrows():
                        roll = str(r["roll_no"]).strip()
                        if current["roll_no"].astype(str).eq(roll).any():
                            continue
                        save_student(
                            roll, str(r["student_name"]).strip(),
                            str(r["department"]).strip(),
                            int(r["graduation_year"]),
                            str(r["eligible"]).strip().lower()
                            in ("1", "true", "yes")
                        )
                        current = get_students()
                imported_any = True

            if skill_file is not None:
                df = pd.read_csv(skill_file)
                if "skill_name" not in df.columns:
                    raise ValueError("Skills CSV needs a skill_name column.")
                for skill in df["skill_name"].dropna().astype(str):
                    try:
                        save_skill(skill.strip())
                    except Exception as e:
                        if "duplicate" not in str(e).lower():
                            raise
                imported_any = True

            if placement_file is not None:
                df = pd.read_csv(placement_file, dtype={"roll_no": str})
                required = {
                    "roll_no", "company", "role",
                    "package_lpa", "placement_year"
                }
                if not required.issubset(df.columns):
                    raise ValueError(
                        "Placements CSV is missing required columns."
                    )
                current_students = get_students()
                for _, r in df.iterrows():
                    matches = current_students[
                        current_students["roll_no"].astype(str)
                        == str(r["roll_no"]).strip()
                    ]
                    if matches.empty:
                        raise ValueError(
                            f"Student {r['roll_no']} was not found. "
                            "Import students first."
                        )
                    sid = int(matches.iloc[0]["student_id"])
                    if int(matches.iloc[0]["eligible"]) != 1:
                        raise ValueError(
                            f"Student {r['roll_no']} is not eligible."
                        )
                    save_placement(
                        sid, str(r["company"]).strip(),
                        str(r["role"]).strip(),
                        float(r["package_lpa"]), int(r["placement_year"])
                    )
                imported_any = True

            if not imported_any:
                st.warning("Choose at least one CSV file.")
            else:
                st.success("CSV import completed.")
                st.rerun()

        except Exception as e:
            st.error(f"Import failed: {e}")

# =====================================================
# REPORTS
# =====================================================
elif page == "Reports":
    st.subheader("📑 Reports and Downloads")

    st.write(
        "Placement rate = eligible students with placement records "
        "÷ all eligible students × 100."
    )
    st.caption("Package values are measured in lakhs per annum (LPA).")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Students", len(students))
    c2.metric("Placement Records", len(placements))
    c3.metric("Placement Rate", f"{placement_rate:.1f}%")

    st.subheader("Download Reports")

    st.download_button(
        "⬇️ Download Student Report",
        students.to_csv(index=False).encode("utf-8"),
        "student_report.csv", "text/csv"
    )
    st.download_button(
        "⬇️ Download Placement Report",
        placements.to_csv(index=False).encode("utf-8"),
        "placement_report.csv", "text/csv"
    )

    skills_report = get_skill_demand()
    st.download_button(
        "⬇️ Download Skill Report",
        skills_report.to_csv(index=False).encode("utf-8"),
        "skill_report.csv", "text/csv"
    )

    if not placements.empty:
        dept_report = placements.groupby("department").agg(
            Students_Placed=("student_id", "nunique"),
            Average_Package_LPA=("package_lpa", "mean"),
            Median_Package_LPA=("package_lpa", "median"),
            Highest_Package_LPA=("package_lpa", "max")
        ).reset_index().round(2)

        st.download_button(
            "⬇️ Download Department and Package Report",
            dept_report.to_csv(index=False).encode("utf-8"),
            "department_package_report.csv", "text/csv"
        )
        st.subheader("Department and Package Summary")
        st.dataframe(dept_report, use_container_width=True, hide_index=True)

# =====================================================
# FOOTER
# =====================================================
st.sidebar.divider()
st.sidebar.caption("Student Placement Data Analysis System")
st.sidebar.caption("Academic Project • PlacementIQ")

if conn is not None and conn.is_connected():
    conn.close()
