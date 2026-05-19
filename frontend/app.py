import pandas as pd
import requests
import streamlit as st

from api_client import BASE_URL, get, post

st.set_page_config(
    page_title="Student Digital Guardian",
    layout="wide",
    initial_sidebar_state="expanded",
)


APP_OPTIONS = [
    "YouTube",
    "Instagram",
    "WhatsApp",
    "Game",
    "Chrome",
    "Study App",
]

MENU_OPTIONS = [
    "Overview",
    "Register",
    "Login",
    "Pair Student",
    "Add Usage",
    "Dashboard",
    "Alerts",
    "AI Chatbot",
    "Daily Report",
]


def inject_styles():
    st.markdown(
        """
        <style>
        :root {
            --bg: #0b1220;
            --panel: rgba(15, 23, 42, 0.78);
            --panel-strong: rgba(17, 24, 39, 0.92);
            --line: rgba(148, 163, 184, 0.18);
            --text: #e5eefc;
            --muted: #9fb1cd;
            --accent: #33d1b6;
            --accent-2: #ff8f5c;
            --accent-3: #7cc8ff;
            --danger: #ff6b7d;
            --warning: #fbbf24;
            --success: #2ed47a;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(51, 209, 182, 0.16), transparent 28%),
                radial-gradient(circle at top right, rgba(124, 200, 255, 0.16), transparent 22%),
                linear-gradient(180deg, #08101c 0%, #0c1424 45%, #09111d 100%);
            color: var(--text);
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(8, 16, 28, 0.98), rgba(12, 20, 36, 0.96));
            border-right: 1px solid var(--line);
        }

        [data-testid="stForm"],
        [data-testid="stMetric"],
        div[data-testid="stDataFrame"],
        div[data-testid="stCodeBlock"] {
            border-radius: 18px;
        }

        .hero {
            padding: 2rem 2.2rem;
            border: 1px solid var(--line);
            border-radius: 28px;
            background:
                linear-gradient(135deg, rgba(51, 209, 182, 0.16), rgba(17, 24, 39, 0.05) 38%),
                linear-gradient(135deg, rgba(124, 200, 255, 0.1), rgba(255, 143, 92, 0.12));
            box-shadow: 0 24px 80px rgba(0, 0, 0, 0.22);
            margin-bottom: 1.5rem;
        }

        .hero-title {
            font-size: 3rem;
            line-height: 1.02;
            font-weight: 800;
            letter-spacing: -0.04em;
            margin: 0 0 0.7rem 0;
            color: #f8fbff;
        }

        .hero-copy {
            max-width: 50rem;
            font-size: 1.05rem;
            line-height: 1.75;
            color: var(--muted);
            margin: 0;
        }

        .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.7rem;
            margin-top: 1.25rem;
        }

        .chip {
            padding: 0.5rem 0.85rem;
            border-radius: 999px;
            background: rgba(15, 23, 42, 0.68);
            border: 1px solid var(--line);
            color: #d5e4fb;
            font-size: 0.92rem;
        }

        .section-card,
        .metric-card,
        .status-card {
            border: 1px solid var(--line);
            background: var(--panel);
            border-radius: 22px;
            padding: 1.15rem 1.2rem;
            box-shadow: 0 18px 55px rgba(0, 0, 0, 0.14);
        }

        .section-title {
            font-size: 1.35rem;
            font-weight: 700;
            color: #f5f9ff;
            margin-bottom: 0.35rem;
        }

        .section-copy {
            color: var(--muted);
            margin-bottom: 0;
        }

        .metric-card {
            min-height: 132px;
        }

        .metric-label {
            font-size: 0.84rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--muted);
            margin-bottom: 0.7rem;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 800;
            color: #f8fbff;
            line-height: 1;
            margin-bottom: 0.55rem;
        }

        .metric-note {
            color: #bfd0ea;
            font-size: 0.95rem;
        }

        .status-card {
            background: var(--panel-strong);
        }

        .status-title {
            font-size: 0.9rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.5rem;
        }

        .status-value {
            font-size: 1.2rem;
            font-weight: 700;
            color: #f8fbff;
        }

        .report-card {
            border-left: 4px solid var(--accent);
        }

        .report-card .section-copy {
            white-space: pre-wrap;
        }

        .empty-state {
            border: 1px dashed rgba(159, 177, 205, 0.35);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            color: var(--muted);
            background: rgba(15, 23, 42, 0.45);
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 999px;
            border: 1px solid rgba(51, 209, 182, 0.5);
            background: linear-gradient(135deg, rgba(51, 209, 182, 0.22), rgba(124, 200, 255, 0.16));
            color: #f8fbff;
            padding: 0.55rem 1.1rem;
            font-weight: 600;
        }

        .stButton > button:hover {
            border-color: rgba(124, 200, 255, 0.7);
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_state():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "paired_students" not in st.session_state:
        st.session_state.paired_students = []


def user():
    return st.session_state.user


def logged_in():
    return user() is not None


def is_parent():
    return logged_in() and user()["role"] == "parent"


def is_student():
    return logged_in() and user()["role"] == "student"


def render_hero():
    st.markdown(
        f"""
        <section class="hero">
            <div class="hero-title">Agentic AI Student Digital Guardian</div>
            <p class="hero-copy">
                A live demo workspace for parent visibility, student activity tracking,
                proactive alerts, and AI-assisted guidance. The current deployment is
                connected to <strong>{BASE_URL}</strong>.
            </p>
            <div class="chip-row">
                <span class="chip">Parent dashboard</span>
                <span class="chip">Student pairing</span>
                <span class="chip">Usage simulation</span>
                <span class="chip">Alerts and reports</span>
                <span class="chip">AI chatbot</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_section_intro(title: str, copy: str):
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">{title}</div>
            <p class="section-copy">{copy}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, note: str):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_card(label: str, value: str):
    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-title">{label}</div>
            <div class="status-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(message: str):
    st.markdown(f'<div class="empty-state">{message}</div>', unsafe_allow_html=True)


def parse_error(error: Exception) -> str:
    if isinstance(error, requests.Timeout):
        return (
            "The backend took too long to respond. On Render free tier this usually means "
            "the API is waking up from sleep. Please wait a moment and try again."
        )
    if isinstance(error, requests.HTTPError) and error.response is not None:
        try:
            payload = error.response.json()
        except ValueError:
            payload = None
        detail = payload.get("detail") if isinstance(payload, dict) else error.response.text
        if detail:
            return f"{error.response.status_code}: {detail}"
        return f"{error.response.status_code}: Request failed"
    return str(error)


def load_parent_students(force: bool = False):
    if not is_parent():
        st.session_state.paired_students = []
        return []
    if st.session_state.paired_students and not force:
        return st.session_state.paired_students

    try:
        students = get(f"/auth/parent/{user()['id']}/students")
    except Exception:
        students = []
    st.session_state.paired_students = students
    return students


def get_student_options():
    if is_student():
        current_user = user()
        return {f"{current_user['name']} (You)": current_user["id"]}
    if is_parent():
        students = load_parent_students()
        return {
            f"{student['name']} - ID {student['id']} - {student['pair_code']}": student["id"]
            for student in students
        }
    return {}


def choose_student(label: str, key: str) -> int:
    options = get_student_options()
    if options:
        selected_label = st.selectbox(label, list(options.keys()), key=key)
        return int(options[selected_label])

    st.caption("No linked student context found yet, so this demo is using a manual student ID.")
    return int(st.number_input(label, min_value=1, value=1, step=1, key=f"{key}_manual"))


def show_sidebar():
    with st.sidebar:
        st.markdown("### Control Center")
        st.caption("Move through the demo from account setup to monitoring.")
        menu = st.radio("Workspace", MENU_OPTIONS, label_visibility="collapsed")
        st.divider()

        current_user = user()
        if current_user:
            render_status_card("Signed In", f"{current_user['name']} ({current_user['role']})")
            st.caption(current_user["email"])
            if current_user.get("pair_code"):
                st.caption(f"Student pair code: {current_user['pair_code']}")
            if st.button("Log Out", use_container_width=True):
                st.session_state.user = None
                st.session_state.paired_students = []
                st.rerun()
        else:
            render_status_card("Session", "Guest mode")
            st.caption("Register or log in to unlock role-aware flows.")

        return menu


def render_overview():
    render_section_intro(
        "Presentation-ready flow",
        "Use this screen to walk someone through the product before you start clicking. "
        "The app adapts once a parent or student account is active.",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card("Accounts", "Parent + Student", "Create one of each to test pairing end to end.")
    with col2:
        render_metric_card("Monitoring", "Usage + Alerts", "Simulate screen-time activity and watch risk signals update.")
    with col3:
        render_metric_card("Support", "AI Guidance", "Ask questions about activity patterns and generate daily summaries.")

    st.markdown("")
    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        render_section_intro(
            "Suggested demo order",
            "Register a student, note the pair code, register a parent, pair them together, "
            "then add usage and open the dashboard, alerts, chatbot, and daily report.",
        )
    with right:
        current_user = user()
        if current_user:
            render_section_intro(
                "Current session",
                f"You are signed in as {current_user['name']} with the {current_user['role']} role.",
            )
        else:
            render_section_intro(
                "Current session",
                "You are in guest mode. The navigation on the left is ready whenever you want to start the flow.",
            )


def render_register():
    render_section_intro(
        "Create an account",
        "Set up either a parent profile for monitoring or a student profile that generates a pair code.",
    )

    with st.form("register_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", placeholder="Akhila")
            email = st.text_input("Email", placeholder="name@example.com")
        with col2:
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["parent", "student"])
        submitted = st.form_submit_button("Create account")

    if submitted:
        try:
            data = post(
                "/auth/register",
                {"name": name, "email": email, "password": password, "role": role},
            )
            st.success("Registration successful.")
            col1, col2 = st.columns(2)
            with col1:
                render_status_card("New user", data["name"])
            with col2:
                render_status_card("Role", data["role"].title())
            if data.get("pair_code"):
                st.info(f"Student pair code: {data['pair_code']}")
        except Exception as error:
            st.error(parse_error(error))


def render_login():
    render_section_intro(
        "Log into the live deployment",
        "Use an account created inside this Render database. Parent accounts unlock pairing and monitoring views.",
    )

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="name@example.com")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

    if submitted:
        try:
            data = post("/auth/login", {"email": email, "password": password})
            st.session_state.user = data
            if data["role"] == "parent":
                load_parent_students(force=True)
            else:
                st.session_state.paired_students = []
            st.success(f"Logged in as {data['name']} ({data['role']}).")
            st.rerun()
        except Exception as error:
            st.error(parse_error(error))

    if logged_in():
        col1, col2, col3 = st.columns(3)
        with col1:
            render_status_card("Signed in", user()["name"])
        with col2:
            render_status_card("Role", user()["role"].title())
        with col3:
            render_status_card("User ID", str(user()["id"]))


def render_pair_student():
    render_section_intro(
        "Connect a parent to a student",
        "Parents can pair with a student using the student account's generated pair code.",
    )

    if not is_parent():
        render_empty_state("Log in as a parent account first to connect a student.")
        return

    with st.form("pair_form", clear_on_submit=True):
        pair_code = st.text_input("Student pair code", placeholder="STU12345")
        submitted = st.form_submit_button("Connect student")

    if submitted:
        try:
            data = post("/auth/pair", {"parent_id": user()["id"], "pair_code": pair_code})
            load_parent_students(force=True)
            st.success(data["message"])
            render_status_card("Connected student", f"{data['student_name']} (ID {data['student_id']})")
        except Exception as error:
            st.error(parse_error(error))

    students = load_parent_students(force=True)
    st.markdown("")
    if students:
        st.subheader("Linked students")
        student_df = pd.DataFrame(students).rename(
            columns={
                "id": "Student ID",
                "name": "Name",
                "email": "Email",
                "pair_code": "Pair Code",
            }
        )
        st.dataframe(student_df, use_container_width=True, hide_index=True)
    else:
        render_empty_state("No students linked yet. Pair a student code to unlock dashboard data.")


def render_add_usage():
    render_section_intro(
        "Simulate app activity",
        "Feed usage events into the workflow to trigger agent analysis, alerts, and dashboard updates.",
    )

    with st.form("usage_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            student_id = choose_student("Student", "usage_student")
            app_name = st.selectbox("App", APP_OPTIONS)
        with col2:
            duration = st.number_input("Duration in minutes", min_value=1, value=30)
            limit = st.number_input("Daily limit in minutes", min_value=1, value=60)
        submitted = st.form_submit_button("Save usage event")

    if submitted:
        try:
            data = post(
                "/usage/add",
                {
                    "student_id": int(student_id),
                    "app_name": app_name,
                    "duration_minutes": int(duration),
                    "limit_minutes": int(limit),
                },
            )
            st.success("Usage event saved.")
            usage = data["usage"]
            alert = data["alert"]
            col1, col2, col3 = st.columns(3)
            with col1:
                render_status_card("Student ID", str(usage["student_id"]))
            with col2:
                render_status_card("App tracked", usage["app_name"])
            with col3:
                render_status_card("Blocked", "Yes" if usage["is_blocked"] else "No")

            if usage["is_blocked"]:
                st.error(alert["message"])
            else:
                st.info(alert["message"])

            with st.expander("Agent workflow output"):
                st.json(data["agent_workflow"])
        except Exception as error:
            st.error(parse_error(error))


def render_dashboard():
    render_section_intro(
        "Usage dashboard",
        "Review tracked app activity, total minutes, and app-by-app distribution for a selected student.",
    )

    student_id = choose_student("Student", "dashboard_student")
    if st.button("Load dashboard", use_container_width=False):
        try:
            usage = get(f"/usage/student/{student_id}")
            summary = get(f"/usage/student/{student_id}/summary")

            total_minutes = sum(summary.values())
            blocked_count = sum(1 for row in usage if row["is_blocked"])
            col1, col2, col3 = st.columns(3)
            with col1:
                render_metric_card("Total minutes", str(total_minutes), "Combined tracked usage across all apps.")
            with col2:
                render_metric_card("Tracked apps", str(len(summary)), "Unique apps with recorded activity.")
            with col3:
                render_metric_card("Blocked sessions", str(blocked_count), "Usage events that crossed the configured limit.")

            st.markdown("")
            if usage:
                usage_df = pd.DataFrame(usage).rename(
                    columns={
                        "id": "Event ID",
                        "student_id": "Student ID",
                        "app_name": "App",
                        "duration_minutes": "Minutes",
                        "limit_minutes": "Limit",
                        "opened_at": "Opened At",
                        "is_blocked": "Blocked",
                    }
                )
                st.dataframe(usage_df, use_container_width=True, hide_index=True)
            else:
                render_empty_state("No usage data found for this student yet.")

            if summary:
                st.subheader("Usage summary")
                summary_df = pd.DataFrame(list(summary.items()), columns=["App", "Minutes"]).set_index("App")
                st.bar_chart(summary_df)
            else:
                render_empty_state("A summary chart will appear after the first usage event is added.")
        except Exception as error:
            st.error(parse_error(error))


def render_alerts():
    render_section_intro(
        "Alerts feed",
        "See the warnings produced by the usage agent workflow, ordered from newest to oldest.",
    )

    student_id = choose_student("Student", "alerts_student")
    if st.button("Load alerts", use_container_width=False):
        try:
            alerts = get(f"/alerts/student/{student_id}")
            if alerts:
                high_count = sum(1 for alert in alerts if alert["severity"].lower() == "high")
                col1, col2 = st.columns(2)
                with col1:
                    render_metric_card("Total alerts", str(len(alerts)), "All recorded alerts for the selected student.")
                with col2:
                    render_metric_card("High severity", str(high_count), "Alerts that may need faster parent action.")

                alert_df = pd.DataFrame(alerts).rename(
                    columns={
                        "id": "Alert ID",
                        "student_id": "Student ID",
                        "app_name": "App",
                        "message": "Message",
                        "severity": "Severity",
                        "created_at": "Created At",
                    }
                )
                st.dataframe(alert_df, use_container_width=True, hide_index=True)
            else:
                render_empty_state("No alerts have been generated for this student yet.")
        except Exception as error:
            st.error(parse_error(error))


def render_chatbot():
    render_section_intro(
        "AI guardian assistant",
        "Ask for a behavior summary, intervention ideas, or a quick explanation of the student's current app pattern.",
    )

    with st.form("chatbot_form", clear_on_submit=False):
        student_id = choose_student("Student", "chat_student")
        question = st.text_area(
            "Question",
            value="What did my child use today, and should I intervene on any app?",
            height=120,
        )
        submitted = st.form_submit_button("Ask the AI guardian")

    if submitted:
        try:
            data = post("/chatbot/ask", {"student_id": int(student_id), "question": question})
            st.subheader("AI answer")
            st.markdown(
                f'<div class="section-card report-card"><p class="section-copy">{data["answer"]}</p></div>',
                unsafe_allow_html=True,
            )
            if data["usage_summary"]:
                summary_df = pd.DataFrame(
                    list(data["usage_summary"].items()),
                    columns=["App", "Minutes"],
                )
                st.subheader("Usage context sent to the AI")
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
            else:
                render_empty_state("The AI used an empty usage summary because no activity has been recorded yet.")
        except Exception as error:
            st.error(parse_error(error))


def render_daily_report():
    render_section_intro(
        "Daily report",
        "Generate a plain-language summary that you can read out or share during a parent demo.",
    )

    student_id = choose_student("Student", "report_student")
    if st.button("Generate report", use_container_width=False):
        try:
            data = get(f"/reports/student/{student_id}/daily")
            st.markdown(
                f'<div class="section-card report-card"><div class="section-title">Report</div>'
                f'<p class="section-copy">{data["report"]}</p></div>',
                unsafe_allow_html=True,
            )
        except Exception as error:
            st.error(parse_error(error))


initialize_state()
inject_styles()
menu = show_sidebar()
render_hero()

if menu == "Overview":
    render_overview()
elif menu == "Register":
    render_register()
elif menu == "Login":
    render_login()
elif menu == "Pair Student":
    render_pair_student()
elif menu == "Add Usage":
    render_add_usage()
elif menu == "Dashboard":
    render_dashboard()
elif menu == "Alerts":
    render_alerts()
elif menu == "AI Chatbot":
    render_chatbot()
elif menu == "Daily Report":
    render_daily_report()
