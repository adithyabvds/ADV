
import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------

st.set_page_config(
    page_title="Student Attendance Dashboard",
    page_icon="🎓",
    layout="wide"
)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("student_attendance_clean.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# -------------------------------------------------
# TITLE
# -------------------------------------------------

st.title("🎓 Real-Time Student Attendance Dashboard")
st.write("Present/Absent Students | Department-wise Attendance")

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------

st.sidebar.header("🔎 Filters")

# Date filter
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Department filter
departments = sorted(df["Department"].dropna().unique())

selected_departments = st.sidebar.multiselect(
    "Select Department",
    options=departments,
    default=departments
)

# Attendance status filter
statuses = sorted(df["AttendanceStatus"].dropna().unique())

selected_statuses = st.sidebar.multiselect(
    "Select Attendance Status",
    options=statuses,
    default=statuses
)

# -------------------------------------------------
# FILTER DATA
# -------------------------------------------------

filtered_df = df.copy()

if len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["Date"].dt.date >= start_date) &
        (filtered_df["Date"].dt.date <= end_date)
    ]

filtered_df = filtered_df[
    filtered_df["Department"].isin(selected_departments)
]

filtered_df = filtered_df[
    filtered_df["AttendanceStatus"].isin(selected_statuses)
]

# -------------------------------------------------
# KPI CALCULATIONS
# -------------------------------------------------

total_students = filtered_df["StudentID"].nunique()

present_records = filtered_df[
    filtered_df["AttendanceStatus"]
    .str.strip()
    .str.lower()
    .eq("present")
]

absent_records = filtered_df[
    filtered_df["AttendanceStatus"]
    .str.strip()
    .str.lower()
    .eq("absent")
]

present_count = len(present_records)
absent_count = len(absent_records)

total_records = len(filtered_df)

if total_records > 0:
    attendance_percentage = (
        present_count / total_records * 100
    )
else:
    attendance_percentage = 0

# -------------------------------------------------
# KPI CARDS
# -------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "👨‍🎓 Total Students",
    f"{total_students:,}"
)

col2.metric(
    "🟢 Present Records",
    f"{present_count:,}"
)

col3.metric(
    "🔴 Absent Records",
    f"{absent_count:,}"
)

col4.metric(
    "📊 Attendance %",
    f"{attendance_percentage:.2f}%"
)

# -------------------------------------------------
# ATTENDANCE STATUS PIE CHART
# -------------------------------------------------

st.subheader("🥧 Present vs Absent Attendance")

status_counts = (
    filtered_df
    .groupby("AttendanceStatus")
    .size()
    .reset_index(name="Count")
)

if not status_counts.empty:
    fig1 = px.pie(
        status_counts,
        names="AttendanceStatus",
        values="Count",
        title="Attendance Distribution"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )
else:
    st.warning("No data available for the selected filters.")

# -------------------------------------------------
# DEPARTMENT-WISE ATTENDANCE
# -------------------------------------------------

st.subheader("🏢 Department-wise Attendance")

dept_df = filtered_df.copy()

dept_df["IsPresent"] = (
    dept_df["AttendanceStatus"]
    .str.strip()
    .str.lower()
    .eq("present")
)

department_attendance = (
    dept_df
    .groupby("Department")
    .agg(
        Total_Records=("StudentID", "count"),
        Present=("IsPresent", "sum")
    )
    .reset_index()
)

if not department_attendance.empty:

    department_attendance["Attendance_Percentage"] = (
        department_attendance["Present"]
        / department_attendance["Total_Records"]
        * 100
    )

    fig2 = px.bar(
        department_attendance,
        x="Department",
        y="Attendance_Percentage",
        title="Department-wise Attendance Percentage",
        text_auto=".2f"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# -------------------------------------------------
# PRESENT VS ABSENT BY DEPARTMENT
# -------------------------------------------------

st.subheader("📊 Present vs Absent by Department")

department_status = (
    filtered_df
    .groupby(
        ["Department", "AttendanceStatus"]
    )
    .size()
    .reset_index(name="Count")
)

if not department_status.empty:

    fig3 = px.bar(
        department_status,
        x="Department",
        y="Count",
        color="AttendanceStatus",
        barmode="group",
        title="Department Attendance Comparison"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

# -------------------------------------------------
# DAILY ATTENDANCE TREND
# -------------------------------------------------

st.subheader("📈 Daily Attendance Trend")

daily_attendance = (
    filtered_df
    .groupby(
        ["Date", "AttendanceStatus"]
    )
    .size()
    .reset_index(name="Count")
)

if not daily_attendance.empty:

    fig4 = px.line(
        daily_attendance,
        x="Date",
        y="Count",
        color="AttendanceStatus",
        title="Daily Attendance Trend"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

# -------------------------------------------------
# DEPARTMENT ATTENDANCE TABLE
# -------------------------------------------------

st.subheader("📋 Department Attendance Summary")

if not department_attendance.empty:

    department_attendance["Absent"] = (
        department_attendance["Total_Records"]
        - department_attendance["Present"]
    )

    department_attendance = (
        department_attendance[
            [
                "Department",
                "Total_Records",
                "Present",
                "Absent",
                "Attendance_Percentage"
            ]
        ]
        .sort_values(
            "Attendance_Percentage",
            ascending=False
        )
    )

    st.dataframe(
        department_attendance,
        use_container_width=True
    )

# -------------------------------------------------
# FILTERED DATA
# -------------------------------------------------

st.subheader("📚 Student Attendance Data")

st.dataframe(
    filtered_df,
    use_container_width=True
)
