
import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector
from mysql.connector import Error

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="PlacementIQ | Analytics Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. CSS STYLING - READABLE TEXT AND BUTTONS
# =====================================================
st.markdown("""
<style>
    .stApp {
        background-color: #f5f7fb;
        color: #1f2937;
    }

    /* Headings */
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4 {
        color: #1e3a8a !important;
        font-weight: 700;
    }

    /* Main page text */
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] li,
    .stApp [data-testid="stWidgetLabel"] p,
    .stApp label {
        color: #1f2937;
    }

    /* Sidebar */
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

    /* Input fields */
    .stApp input,
    .stApp textarea {
        color: #111827 !important;
        background-color: #ffffff !important;
    }

    .stApp [data-baseweb="select"] > div {
        background-color: #ffffff !important;
    }

    .stApp [data-baseweb="select"] span {
        color: #111827 !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"] {
        color: #111827 !important;
    }

    /* ALL BUTTONS: BLUE BACKGROUND + WHITE TEXT */
    .stApp button,
    .stApp button p,
    .stApp button span,
    .stApp button div {
        color: #ffffff !important;
    }

    .stApp div.stButton > button,
    .stApp div.stFormSubmitButton > button,
    .stApp button[kind="primary"],
    .stApp button[kind="secondary"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #1d4ed8 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 10px 18px !important;
    }

    .stApp div.stButton > button:hover,
    .stApp div.stFormSubmitButton > button:hover {
        background-color: #1d4ed8 !important;
        border-color: #1e40af !important;
    }

    /* Charts */
    div[data-testid="stPlotlyChart"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 8px;
        border: 1px solid #e2e8f0;
    }

    /* Data tables */
    [data-testid="stDataFrame"] {
        background-color: #ffffff;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. HEADER
# =====================================================
st.title("🎓 PlacementIQ")
st.markdown(
    "**STUDENT PLACEMENT DATA ANALYSIS SYSTEM**  \n"
    "Analyze placement outcomes, package trends, departments and skills."
)
st.divider()

# =====================================================
# 4. DATABASE CONNECTION
# =====================================================
st.sidebar.title("🎓 PlacementIQ")
st.sidebar.caption("Student Placement Analytics")
st.sidebar.divider()
st.sidebar.subheader("Database Connection")

db_user = st.sidebar.text_input("MySQL username", value="root")
db_password = st.sidebar.text_input("MySQL password", type="password")

if not db_password:
    st.info("Enter your MySQL password in the sidebar to continue.")
    st.stop()

try:
    conn = mysql.connector.connect(
        host="localhost",
        user=db_user,
        password=db_password,
        database="placement_db"
    )
    st.sidebar.success("Database connected")
except Error as e:
    st.error(f"Database connection failed: {e}")
    st.stop()


# =====================================================
# 5. DATABASE HELPER FUNCTIONS
# =====================================================
def read_data(query, params=None):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        return pd.DataFrame(cursor.fetchall())
    finally:
        cursor.close()


def run_query(query, values=()):
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
    return read_data("""
        SELECT student_id, roll_no, student_name, department,
               graduation_year, eligible, placement_status
        FROM students
        ORDER BY student_id
    """)


def get_placements():
    return read_data("""
        SELECT p.placement_id, s.student_id, s.roll_no,
               s.student_name, s.department, p.company, p.role,
               p.package_lpa, p.placement_year
        FROM placements p
        JOIN students s ON p.student_id = s.student_id
        ORDER BY p.placement_year DESC, p.placement_id DESC
    """)


# =====================================================
# 6. SIDEBAR NAVIGATION
# =====================================================
page = st.sidebar.radio(
    "📌 Navigation",
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

# =====================================================
# 7. LOAD DATA AND METRICS
# =====================================================
try:
    students = get_students()
    placements = get_placements()
except Error as e:
    st.error(f"Could not load records: {e}")
    st.stop()

eligible_count = (
    int(students["eligible"].astype(int).sum())
    if not students.empty else 0
)

if not students.empty and not placements.empty:
    eligible_ids = set(
        students.loc[
            students["eligible"].astype(int) == 1,
            "student_id"
        ].astype(int)
    )
    placed_ids = set(placements["student_id"].astype(int))
    eligible_placed_count = len(eligible_ids & placed_ids)
else:
    eligible_placed_count = 0

placement_rate = (
    eligible_placed_count / eligible_count * 100
    if eligible_count else 0
)

# =====================================================
# 8. OVERVIEW
# =====================================================
if page == "Overview":
    st.subheader("📊 Placement Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Students", len(students))
    c2.metric("Eligible Students", eligible_count)
    c3.metric("Eligible Students Placed", eligible_placed_count)
    c4.metric("Placement Rate", f"{placement_rate:.1f}%")

    st.caption(
        "Placement Rate = Eligible students with placement records "
        "÷ Total eligible students × 100."
    )

    if not students.empty:
        dept = students.groupby("department").agg(
            Total_Students=("student_id", "count"),
            Eligible_Students=("eligible", "sum")
        ).reset_index()

        if not placements.empty:
            eligible_ids = set(
                students.loc[
                    students["eligible"].astype(int) == 1,
                    "student_id"
                ].astype(int)
            )
            valid_placements = placements[
                placements["student_id"].astype(int).isin(eligible_ids)
            ]
            placed_dept = (
                valid_placements.groupby("department")
                .size()
                .reset_index(name="Placed_Students")
            )
        else:
            placed_dept = pd.DataFrame(
                columns=["department", "Placed_Students"]
            )

        dept = dept.merge(placed_dept, on="department", how="left")
        dept["Placed_Students"] = (
            dept["Placed_Students"].fillna(0).astype(int)
        )
        dept["Placement_Rate"] = (
            dept["Placed_Students"]
            / dept["Eligible_Students"].replace(0, float("nan"))
            * 100
        ).fillna(0).round(2)

        left, right = st.columns(2)

        with left:
            st.plotly_chart(
                px.bar(
                    dept,
                    x="department",
                    y="Total_Students",
                    color="department",
                    title="Students by Department"
                ),
                use_container_width=True
            )

        with right:
            st.plotly_chart(
                px.bar(
                    dept,
                    x="department",
                    y="Placement_Rate",
                    color="department",
                    title="Placement Rate by Department",
                    labels={"Placement_Rate": "Placement Rate (%)"}
                ),
                use_container_width=True
            )

    st.subheader("🕒 Recent Placements")
    if not placements.empty:
        st.dataframe(
            placements.head(10),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No placement records available yet.")

# =====================================================
# 9. STUDENTS
# =====================================================
elif page == "Students":
    st.subheader("👨‍🎓 Student Management")

    with st.expander("➕ Add a Student", expanded=True):
        with st.form("student_form"):
            roll = st.text_input("Roll Number")
            name = st.text_input("Student Name")

            dept_choice = st.selectbox(
                "Department",
                ["CSE", "ECE", "EEE", "IT", "MECH", "CIVIL", "Other"]
            )

            if dept_choice == "Other":
                department = st.text_input("Enter Department Name")
            else:
                department = dept_choice

            graduation_year = st.number_input(
                "Graduation Year",
                min_value=2026,
                max_value=2040,
                value=2029
            )

            eligible = st.checkbox(
                "Eligible for placements",
                value=True
            )

            submitted = st.form_submit_button(
                "Save Student",
                type="primary",
                use_container_width=True
            )

            if submitted:
                if not roll.strip() or not name.strip() or not department.strip():
                    st.error("Please fill in all required fields.")
                else:
                    try:
                        run_query("""
                            INSERT INTO students
                            (roll_no, student_name, department,
                             graduation_year, eligible, placement_status)
                            VALUES (%s, %s, %s, %s, %s, 'Not Placed')
                        """, (
                            roll.strip(),
                            name.strip(),
                            department.strip(),
                            int(graduation_year),
                            int(eligible)
                        ))
                        st.success("Student added successfully!")
                        st.rerun()
                    except Error as e:
                        st.error(f"Could not add student: {e}")

    st.subheader("📋 Student Records")

    if not students.empty:
        search = st.text_input("Search by roll number, name or department")
        filtered = students

        if search.strip():
            mask = students.astype(str).apply(
                lambda col: col.str.contains(
                    search.strip(), case=False, na=False, regex=False
                )
            ).any(axis=1)
            filtered = students[mask]

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Download Student CSV",
            filtered.to_csv(index=False).encode("utf-8"),
            "students.csv",
            "text/csv"
        )
    else:
        st.info("No student records available.")

# =====================================================
# 10. PLACEMENTS
# =====================================================
elif page == "Placements":
    st.subheader("💼 Placement Management")

    if students.empty:
        st.warning("Add students before recording placements.")
    else:
        placed_ids = (
            set(placements["student_id"].astype(int))
            if not placements.empty else set()
        )

        eligible_students = students[
            (students["eligible"].astype(int) == 1)
            & (~students["student_id"].astype(int).isin(placed_ids))
        ]

        if eligible_students.empty:
            st.info("No eligible unplaced students are available.")
        else:
            with st.form("placement_form"):
                student_map = {
                    f"{r.roll_no} — {r.student_name} ({r.department})":
                    int(r.student_id)
                    for r in eligible_students.itertuples()
                }

                selected = st.selectbox(
                    "Select Student", list(student_map.keys())
                )
                company = st.text_input("Company Name")
                role = st.text_input("Job Role")

                package = st.number_input(
                    "Package (LPA)",
                    min_value=0.01,
                    max_value=1000.0,
                    value=6.0,
                    step=0.5
                )

                year = st.number_input(
                    "Placement Year",
                    min_value=2020,
                    max_value=2040,
                    value=2026
                )

                submitted = st.form_submit_button(
                    "Save Placement",
                    type="primary",
                    use_container_width=True
                )

                if submitted:
                    if not company.strip() or not role.strip():
                        st.error("Enter the company name and job role.")
                    else:
                        cursor = None
                        try:
                            cursor = conn.cursor()
                            sid = student_map[selected]

                            cursor.execute("""
                                INSERT INTO placements
                                (student_id, company, role,
                                 package_lpa, placement_year)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (
                                sid, company.strip(), role.strip(),
                                float(package), int(year)
                            ))

                            cursor.execute("""
                                UPDATE students
                                SET placement_status = 'Placed'
                                WHERE student_id = %s
                            """, (sid,))

                            conn.commit()
                            st.success("Placement saved successfully!")
                            st.rerun()
                        except Error as e:
                            conn.rollback()
                            st.error(f"Could not save placement: {e}")
                        finally:
                            if cursor is not None:
                                cursor.close()

    st.subheader("📋 Placement Records")
    if not placements.empty:
        st.dataframe(
            placements,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No placement records available.")

# =====================================================
# 11. DEPARTMENT ANALYSIS
# =====================================================
elif page == "Department Analysis":
    st.subheader("🏢 Department-wise Analysis")

    if students.empty:
        st.info("Add student records to view department analysis.")
    else:
        dept = students.groupby("department").agg(
            Total_Students=("student_id", "count"),
            Eligible_Students=("eligible", "sum")
        ).reset_index()

        if not placements.empty:
            eligible_ids = set(
                students.loc[
                    students["eligible"].astype(int) == 1,
                    "student_id"
                ].astype(int)
            )
            valid = placements[
                placements["student_id"].astype(int).isin(eligible_ids)
            ]
            placed = (
                valid.groupby("department")
                .size()
                .reset_index(name="Placed_Students")
            )
        else:
            placed = pd.DataFrame(
                columns=["department", "Placed_Students"]
            )

        dept = dept.merge(placed, on="department", how="left")
        dept["Placed_Students"] = (
            dept["Placed_Students"].fillna(0).astype(int)
        )
        dept["Placement_Rate_%"] = (
            dept["Placed_Students"]
            / dept["Eligible_Students"].replace(0, float("nan"))
            * 100
        ).fillna(0).round(2)

        st.dataframe(
            dept,
            use_container_width=True,
            hide_index=True
        )

        st.plotly_chart(
            px.bar(
                dept,
                x="department",
                y="Placement_Rate_%",
                color="department",
                title="Placement Rate by Department"
            ),
            use_container_width=True
        )

        comparison = dept.melt(
            id_vars="department",
            value_vars=["Eligible_Students", "Placed_Students"],
            var_name="Student Category",
            value_name="Number of Students"
        )

        st.plotly_chart(
            px.bar(
                comparison,
                x="department",
                y="Number of Students",
                color="Student Category",
                barmode="group",
                title="Eligible vs Placed Students"
            ),
            use_container_width=True
        )

# =====================================================
# 12. PACKAGE ANALYTICS
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

            st.plotly_chart(
                px.histogram(
                    placements,
                    x="package_lpa",
                    nbins=10,
                    title="Package Distribution",
                    labels={"package_lpa": "Package (LPA)"}
                ),
                use_container_width=True
            )

            company_summary = (
                placements.groupby("company")
                .agg(
                    Average_Package=("package_lpa", "mean"),
                    Highest_Package=("package_lpa", "max"),
                    Students_Placed=("student_id", "nunique")
                )
                .reset_index()
                .round(2)
            )

            st.plotly_chart(
                px.bar(
                    company_summary,
                    x="company",
                    y="Average_Package",
                    title="Average Package by Company",
                    hover_data=["Highest_Package", "Students_Placed"]
                ),
                use_container_width=True
            )

            st.subheader("Package Statistics")
            stats = pd.DataFrame({
                "Metric": ["Mean", "Median", "Minimum", "Maximum"],
                "Package (LPA)": [
                    packages.mean(),
                    packages.median(),
                    packages.min(),
                    packages.max()
                ]
            }).round(2)

            st.dataframe(stats, use_container_width=True, hide_index=True)

# =====================================================
# 13. SKILL DEMAND
# =====================================================
elif page == "Skill Demand":
    st.subheader("🧠 Skill Management and Demand")

    with st.form("skill_form"):
        skill_name = st.text_input("Skill Name (e.g. Java, SQL, Python)")
        skill_submit = st.form_submit_button(
            "Save Skill",
            type="primary"
        )

        if skill_submit:
            if skill_name.strip():
                try:
                    run_query(
                        "INSERT INTO skills (skill_name) VALUES (%s)",
                        (skill_name.strip(),)
                    )
                    st.success("Skill added successfully!")
                    st.rerun()
                except Error as e:
                    st.error(f"Could not add skill: {e}")
            else:
                st.error("Enter a skill name.")

    skills = read_data("""
        SELECT skill_id, skill_name
        FROM skills
        ORDER BY skill_name
    """)

    if not students.empty and not skills.empty:
        with st.form("student_skill_form"):
            student_map = {
                f"{r.roll_no} — {r.student_name}": int(r.student_id)
                for r in students.itertuples()
            }

            selected_student = st.selectbox(
                "Select Student", list(student_map.keys())
            )
            selected_skill = st.selectbox(
                "Select Skill", skills["skill_name"].tolist()
            )

            assign_submit = st.form_submit_button(
                "Assign Skill",
                type="primary"
            )

            if assign_submit:
                sid = student_map[selected_student]
                kid = int(
                    skills.loc[
                        skills["skill_name"] == selected_skill,
                        "skill_id"
                    ].iloc[0]
                )

                try:
                    run_query("""
                        INSERT INTO student_skills (student_id, skill_id)
                        VALUES (%s, %s)
                    """, (sid, kid))
                    st.success("Skill assigned successfully!")
                    st.rerun()
                except Error as e:
                    st.error(f"Could not assign skill: {e}")

    elif students.empty:
        st.info("Add students before assigning skills.")
    else:
        st.info("Add skills before assigning them.")

    demand = read_data("""
        SELECT sk.skill_name,
               COUNT(DISTINCT ss.student_id) AS students_with_skill
        FROM skills sk
        LEFT JOIN student_skills ss ON sk.skill_id = ss.skill_id
        GROUP BY sk.skill_id, sk.skill_name
        ORDER BY students_with_skill DESC, sk.skill_name
    """)

    st.subheader("📈 Skills Report")
    st.caption(
        "This chart counts skills reported by students; "
        "it does not independently measure employer demand."
    )

    if not demand.empty:
        st.dataframe(
            demand,
            use_container_width=True,
            hide_index=True
        )

        st.plotly_chart(
            px.bar(
                demand,
                x="skill_name",
                y="students_with_skill",
                title="Skills Reported by Students"
            ),
            use_container_width=True
        )

# =====================================================
# 14. DATA IMPORT
# =====================================================
elif page == "Data Import":
    st.subheader("📂 Bulk CSV Data Import")

    st.info(
        "Upload approved or synthetic data. Existing records are not "
        "automatically deleted. Back up your database before bulk importing."
    )

    with st.expander("Required CSV columns"):
        st.code(
            "Students:\n"
            "roll_no,student_name,department,graduation_year,eligible,placement_status\n\n"
            "Skills:\n"
            "skill_name\n\n"
            "Student Skills:\n"
            "roll_no,skill_name\n\n"
            "Placements:\n"
            "roll_no,company,role,package_lpa,placement_year",
            language="text"
        )

    students_file = st.file_uploader(
        "1. Students CSV", type=["csv"], key="csv_students"
    )
    skills_file = st.file_uploader(
        "2. Skills CSV", type=["csv"], key="csv_skills"
    )
    mappings_file = st.file_uploader(
        "3. Student Skills CSV", type=["csv"], key="csv_mappings"
    )
    placements_file = st.file_uploader(
        "4. Placements CSV", type=["csv"], key="csv_placements"
    )

    if st.button("Import Selected Files", type="primary"):
        cursor = None

        try:
            frames = {}
            specifications = {
                "students": (
                    students_file,
                    {
                        "roll_no", "student_name", "department",
                        "graduation_year", "eligible", "placement_status"
                    }
                ),
                "skills": (skills_file, {"skill_name"}),
                "mappings": (mappings_file, {"roll_no", "skill_name"}),
                "placements": (
                    placements_file,
                    {
                        "roll_no", "company", "role",
                        "package_lpa", "placement_year"
                    }
                )
            }

            for name, (uploaded, required) in specifications.items():
                if uploaded is None:
                    continue

                df = pd.read_csv(uploaded, dtype={"roll_no": str})
                df.columns = df.columns.str.strip()
                missing = required - set(df.columns)

                if missing:
                    raise ValueError(
                        f"{name} CSV missing columns: "
                        f"{', '.join(sorted(missing))}"
                    )

                if df.empty:
                    raise ValueError(f"{name} CSV contains no records.")

                if df[list(required)].isnull().any().any():
                    raise ValueError(
                        f"{name} CSV contains empty required values."
                    )

                frames[name] = df

            if not frames:
                raise ValueError("Select at least one CSV file.")

            conn.start_transaction()
            cursor = conn.cursor()

            # Students
            if "students" in frames:
                df = frames["students"]

                if df["roll_no"].astype(str).str.strip().duplicated().any():
                    raise ValueError("Duplicate roll numbers in students CSV.")

                for _, r in df.iterrows():
                    eligible_text = str(r["eligible"]).strip().lower()

                    if eligible_text not in (
                        "0", "1", "true", "false", "yes", "no"
                    ):
                        raise ValueError(
                            f"Invalid eligibility for {r['roll_no']}."
                        )

                    eligible_value = int(
                        eligible_text in ("1", "true", "yes")
                    )

                    cursor.execute("""
                        INSERT INTO students
                        (roll_no, student_name, department,
                         graduation_year, eligible, placement_status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            student_name = VALUES(student_name),
                            department = VALUES(department),
                            graduation_year = VALUES(graduation_year),
                            eligible = VALUES(eligible)
                    """, (
                        str(r["roll_no"]).strip(),
                        str(r["student_name"]).strip(),
                        str(r["department"]).strip(),
                        int(r["graduation_year"]),
                        eligible_value,
                        str(r["placement_status"]).strip()
                    ))

            # Skills
            if "skills" in frames:
                for _, r in frames["skills"].iterrows():
                    cursor.execute("""
                        INSERT IGNORE INTO skills (skill_name)
                        VALUES (%s)
                    """, (str(r["skill_name"]).strip(),))

            # Student skills
            if "mappings" in frames:
                for _, r in frames["mappings"].iterrows():
                    roll = str(r["roll_no"]).strip()
                    skill = str(r["skill_name"]).strip()

                    cursor.execute(
                        "SELECT student_id FROM students WHERE roll_no=%s",
                        (roll,)
                    )
                    student_row = cursor.fetchone()

                    cursor.execute(
                        "SELECT skill_id FROM skills WHERE skill_name=%s",
                        (skill,)
                    )
                    skill_row = cursor.fetchone()

                    if not student_row or not skill_row:
                        raise ValueError(
                            f"Student '{roll}' or skill '{skill}' not found. "
                            "Import students and skills first."
                        )

                    cursor.execute("""
                        INSERT IGNORE INTO student_skills
                        (student_id, skill_id)
                        VALUES (%s, %s)
                    """, (student_row[0], skill_row[0]))

            # Placements
            if "placements" in frames:
                df = frames["placements"]

                if df["roll_no"].astype(str).str.strip().duplicated().any():
                    raise ValueError(
                        "Only one placement per student is supported."
                    )

                for _, r in df.iterrows():
                    package = pd.to_numeric(r["package_lpa"], errors="coerce")
                    year = pd.to_numeric(r["placement_year"], errors="coerce")

                    if pd.isna(package) or package <= 0:
                        raise ValueError("Package must be a positive number.")

                    if pd.isna(year) or int(year) != year:
                        raise ValueError("Placement year must be a whole number.")

                    cursor.execute("""
                        SELECT student_id, eligible
                        FROM students WHERE roll_no=%s
                    """, (str(r["roll_no"]).strip(),))
                    student_row = cursor.fetchone()

                    if not student_row:
                        raise ValueError(
                            f"Student '{r['roll_no']}' not found."
                        )

                    if not int(student_row[1]):
                        raise ValueError(
                            f"Student '{r['roll_no']}' is not eligible."
                        )

                    cursor.execute("""
                        INSERT INTO placements
                        (student_id, company, role, package_lpa, placement_year)
                        VALUES (%s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            company = VALUES(company),
                            role = VALUES(role),
                            package_lpa = VALUES(package_lpa),
                            placement_year = VALUES(placement_year)
                    """, (
                        student_row[0],
                        str(r["company"]).strip(),
                        str(r["role"]).strip(),
                        float(package),
                        int(year)
                    ))

            # Synchronize status with placement records
            cursor.execute("""
                UPDATE students s
                LEFT JOIN placements p ON s.student_id = p.student_id
                SET s.placement_status =
                    CASE
                        WHEN p.placement_id IS NULL THEN 'Not Placed'
                        ELSE 'Placed'
                    END
            """)

            conn.commit()
            cursor.close()
            cursor = None

            st.success("CSV import completed successfully!")
            st.rerun()

        except Exception as e:
            conn.rollback()

            if cursor is not None:
                cursor.close()

            st.error(f"Import failed: {e}")

# =====================================================
# 15. REPORTS
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
        "student_report.csv",
        "text/csv"
    )

    st.download_button(
        "⬇️ Download Placement Report",
        placements.to_csv(index=False).encode("utf-8"),
        "placement_report.csv",
        "text/csv"
    )

    skills_report = read_data("""
        SELECT sk.skill_name,
               COUNT(DISTINCT ss.student_id) AS students_with_skill
        FROM skills sk
        LEFT JOIN student_skills ss ON sk.skill_id = ss.skill_id
        GROUP BY sk.skill_id, sk.skill_name
        ORDER BY students_with_skill DESC, sk.skill_name
    """)

    st.download_button(
        "⬇️ Download Skill Report",
        skills_report.to_csv(index=False).encode("utf-8"),
        "skill_report.csv",
        "text/csv"
    )

    if not placements.empty:
        dept_report = (
            placements.groupby("department")
            .agg(
                Students_Placed=("student_id", "nunique"),
                Average_Package_LPA=("package_lpa", "mean"),
                Median_Package_LPA=("package_lpa", "median"),
                Highest_Package_LPA=("package_lpa", "max")
            )
            .reset_index()
            .round(2)
        )

        st.download_button(
            "⬇️ Download Department and Package Report",
            dept_report.to_csv(index=False).encode("utf-8"),
            "department_package_report.csv",
            "text/csv"
        )

        st.subheader("Department and Package Summary")
        st.dataframe(
            dept_report,
            use_container_width=True,
            hide_index=True
        )

# =====================================================
# 16. FOOTER
# =====================================================
st.sidebar.divider()
st.sidebar.caption("Student Placement Data Analysis System")
st.sidebar.caption("Academic Project • PlacementIQ")
