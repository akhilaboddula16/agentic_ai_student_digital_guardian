import streamlit as st
import pandas as pd
from api_client import post, get

st.set_page_config(page_title="Student Digital Guardian", page_icon="🛡️", layout="wide")

st.title("🛡️ Agentic AI Student Digital Guardian")
st.write("Parent dashboard + simulated student app tracking + AI chatbot")

if "user" not in st.session_state:
    st.session_state.user = None

menu = st.sidebar.radio(
    "Menu",
    ["Register", "Login", "Pair Student", "Add Usage", "Dashboard", "Alerts", "AI Chatbot", "Daily Report"],
)

if menu == "Register":
    st.header("Create Account")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["parent", "student"])

    if st.button("Register"):
        try:
            data = post("/auth/register", {"name": name, "email": email, "password": password, "role": role})
            st.success("Registration successful")
            st.json(data)
            if data.get("role") == "student":
                st.info(f"Student Pair Code: {data.get('pair_code')}")
        except Exception as e:
            st.error(e)

elif menu == "Login":
    st.header("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            data = post("/auth/login", {"email": email, "password": password})
            st.session_state.user = data
            st.success(f"Logged in as {data['name']} ({data['role']})")
            st.json(data)
        except Exception as e:
            st.error(e)

elif menu == "Pair Student":
    st.header("Parent-Student Pairing")
    if not st.session_state.user or st.session_state.user["role"] != "parent":
        st.warning("Login as parent first")
    else:
        pair_code = st.text_input("Enter Student Pair Code")
        if st.button("Connect Student"):
            try:
                data = post("/auth/pair", {"parent_id": st.session_state.user["id"], "pair_code": pair_code})
                st.success(data["message"])
                st.json(data)
            except Exception as e:
                st.error(e)

elif menu == "Add Usage":
    st.header("Simulate Student App Usage")
    student_id = st.number_input("Student ID", min_value=1, value=1)
    app_name = st.selectbox("App", ["YouTube", "Instagram", "WhatsApp", "Game", "Chrome", "Study App"])
    duration = st.number_input("Duration Minutes", min_value=1, value=30)
    limit = st.number_input("Limit Minutes", min_value=1, value=60)

    if st.button("Save Usage"):
        try:
            data = post("/usage/add", {
                "student_id": int(student_id),
                "app_name": app_name,
                "duration_minutes": int(duration),
                "limit_minutes": int(limit),
            })
            st.success("Usage saved")
            if data["usage"]["is_blocked"]:
                st.error(data["alert"]["message"])
            else:
                st.info(data["alert"]["message"])
            with st.expander("Agent Workflow Output"):
                st.json(data["agent_workflow"])
        except Exception as e:
            st.error(e)

elif menu == "Dashboard":
    st.header("Usage Dashboard")
    student_id = st.number_input("Student ID", min_value=1, value=1, key="dash_student")
    if st.button("Load Dashboard"):
        try:
            usage = get(f"/usage/student/{int(student_id)}")
            summary = get(f"/usage/student/{int(student_id)}/summary")
            if usage:
                df = pd.DataFrame(usage)
                st.dataframe(df, use_container_width=True)
                st.subheader("Usage Summary")
                st.bar_chart(pd.DataFrame(list(summary.items()), columns=["App", "Minutes"]).set_index("App"))
            else:
                st.info("No usage data found")
        except Exception as e:
            st.error(e)

elif menu == "Alerts":
    st.header("Parent Alerts")
    student_id = st.number_input("Student ID", min_value=1, value=1, key="alert_student")
    if st.button("Load Alerts"):
        try:
            alerts = get(f"/alerts/student/{int(student_id)}")
            if alerts:
                st.dataframe(pd.DataFrame(alerts), use_container_width=True)
            else:
                st.info("No alerts found")
        except Exception as e:
            st.error(e)

elif menu == "AI Chatbot":
    st.header("Ask AI Guardian")
    student_id = st.number_input("Student ID", min_value=1, value=1, key="chat_student")
    question = st.text_area("Question", "What did my child use today? Should I block any app?")
    if st.button("Ask"):
        try:
            data = post("/chatbot/ask", {"student_id": int(student_id), "question": question})
            st.subheader("AI Answer")
            st.write(data["answer"])
            with st.expander("Usage Summary"):
                st.json(data["usage_summary"])
        except Exception as e:
            st.error(e)

elif menu == "Daily Report":
    st.header("Daily Usage Report")
    student_id = st.number_input("Student ID", min_value=1, value=1, key="report_student")
    if st.button("Generate Report"):
        try:
            data = get(f"/reports/student/{int(student_id)}/daily")
            st.text(data["report"])
        except Exception as e:
            st.error(e)
