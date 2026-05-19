# Student Digital Guardian

A fresher-friendly full-stack project that simulates how parents can monitor student mobile app usage, receive alerts, view reports, and ask an AI assistant for guidance.

This project combines:
- `FastAPI` for the backend API
- `Streamlit` for the frontend dashboard
- `SQLite` for local development
- `Render` / `Streamlit Cloud` friendly deployment setup
- a simple agent-style workflow for risk analysis, decision making, and alert generation

## What This Project Does

The app supports a simple parent-student monitoring flow:

1. A student registers and gets a unique pair code.
2. A parent registers and logs in.
3. The parent pairs with the student using that pair code.
4. App usage is added for the student.
5. The system checks whether usage crossed the allowed limit.
6. Alerts and reports are generated.
7. The parent can ask the AI chatbot for a summary and suggestions.

## Features

- Parent and student registration
- Password hashing with secure login sessions
- Role-aware access control for student, parent, and admin users
- Pair code based parent-student linking
- Simulated app usage tracking
- Usage limit checks
- Alert generation
- Daily usage report
- Groq-powered chatbot with fallback response
- Admin tools for viewing users and resetting demo data
- Simple agent workflow:
  - Monitoring Agent
  - Analysis Agent
  - Decision Agent
  - Action Agent
- Automated backend integration tests
- Android demo skeleton for future real-device integration

## Tech Stack

- Backend: `FastAPI`, `SQLAlchemy`, `Pydantic`
- Frontend: `Streamlit`, `Pandas`
- Database: `SQLite` locally, `PostgreSQL` supported for deployment
- AI: `Groq` via `groq`
- Deployment: `Render`, `Streamlit Community Cloud`

## Project Structure

```text
student-digital-guardian-code/
|-- backend/
|   |-- agents/
|   |-- models/
|   |-- routes/
|   |-- schemas/
|   |-- services/
|   |-- config.py
|   |-- database.py
|   `-- main.py
|-- frontend/
|   |-- api_client.py
|   |-- app.py
|   |-- requirements.txt
|   `-- secrets.toml.example
|-- android_demo/
|-- .env.example
|-- render.yaml
|-- requirements.txt
`-- README.md
```

## Architecture

### Backend

The backend exposes APIs for:
- authentication
- secure bearer-token session validation
- pairing parent and student accounts
- adding usage records
- viewing alerts
- generating daily reports
- chatbot questions
- admin data management

Main entrypoint:
- [backend/main.py](backend/main.py)

### Frontend

The frontend is a Streamlit dashboard where users can:
- register
- log in
- pair students
- add usage
- open dashboard data
- view alerts
- chat with the AI guardian
- generate daily reports

Main entrypoint:
- [frontend/app.py](frontend/app.py)

### Agent Workflow

Whenever usage is added, a small agent pipeline runs:

`Monitoring -> Analysis -> Decision -> Action`

This pipeline:
- receives usage data
- evaluates risk level
- decides whether the app should be blocked
- creates the alert message shown to the parent

Main workflow file:
- [backend/agents/graph.py](backend/agents/graph.py)

## Local Setup

### 1. Create virtual environment

```bash
python -m venv venv
```

### 2. Activate virtual environment

On Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create environment file

```bash
copy .env.example .env
```

### 5. Add your Groq API key

Put your real Groq key in `.env`, not in `.env.example`.

Example:

```env
GROQ_API_KEY=your_real_key_here
GROQ_MODEL=llama-3.1-8b-instant
BACKEND_URL=http://127.0.0.1:8000
TOKEN_TTL_MINUTES=480
REGISTRATION_MODE=open
REGISTRATION_INVITE_CODE=
ADMIN_EMAILS=
```

Notes:
- `DATABASE_URL` is optional for local development
- `ALLOWED_ORIGINS` is optional for local development
- if `GROQ_API_KEY` is empty, the chatbot still works with a fallback response
- set `REGISTRATION_MODE=invite_only` and `REGISTRATION_INVITE_CODE=...` if you want to lock down public signups
- set `ADMIN_EMAILS=you@example.com` to enable the admin console for specific users

## Run Locally

### Start backend

```bash
uvicorn backend.main:app --reload
```

Backend docs:

```text
http://127.0.0.1:8000/docs
```

### Start frontend

Open a second terminal and run:

```bash
streamlit run frontend/app.py
```

The frontend reads `BACKEND_URL` from:
- Streamlit secrets
- environment variables
- `.env`

If not set, it defaults to:

```text
http://127.0.0.1:8000
```

## Demo Flow

Use this order while testing:

1. Register a student account
2. Copy the generated student pair code
3. Register a parent account
4. Log in as parent
5. Pair the student using the pair code
6. Add app usage
7. Open dashboard
8. Check alerts
9. Ask the chatbot
10. Generate the daily report

## Environment Variables

### Local `.env`

```env
GROQ_API_KEY=
GROQ_MODEL=llama-3.1-8b-instant
BACKEND_URL=http://127.0.0.1:8000
DATABASE_URL=sqlite:///./student_guardian.db
ALLOWED_ORIGINS=*
TOKEN_TTL_MINUTES=480
REGISTRATION_MODE=open
REGISTRATION_INVITE_CODE=
ADMIN_EMAILS=
```

### Meaning

- `GROQ_API_KEY`: enables Groq chatbot responses
- `GROQ_MODEL`: optional Groq model override for chatbot requests
- `BACKEND_URL`: frontend target backend URL
- `DATABASE_URL`: database connection string
- `ALLOWED_ORIGINS`: CORS allowed frontend origins
- `TOKEN_TTL_MINUTES`: access token lifetime
- `REGISTRATION_MODE`: `open`, `invite_only`, or `closed`
- `REGISTRATION_INVITE_CODE`: required code when invite-only mode is enabled
- `ADMIN_EMAILS`: comma-separated emails that should receive admin access

## Deployment

This repo is prepared for:
- backend deployment on `Render` or `Railway`
- frontend deployment on `Streamlit Community Cloud`
- full deployment on `Render` using separate services

### Option 1: Backend on Render, frontend on Streamlit Cloud

#### Backend settings

- Build command: `pip install -r backend/requirements.txt`
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

Backend env vars:
- `DATABASE_URL`
- `GROQ_API_KEY`
- `GROQ_MODEL`
- `TOKEN_TTL_MINUTES`
- `REGISTRATION_MODE`
- `REGISTRATION_INVITE_CODE`
- `ADMIN_EMAILS`
- `ALLOWED_ORIGINS`

Health endpoint:

```text
/healthz
```

#### Frontend settings

- App entrypoint: `frontend/app.py`
- Secret:

```toml
BACKEND_URL = "https://your-backend-url"
```

Template file:
- [frontend/secrets.toml.example](frontend/secrets.toml.example)

### Option 2: Deploy everything on Render

This repo includes:
- [render.yaml](render.yaml)

It defines:
- `student-digital-guardian-db`
- `student-digital-guardian-api`
- `student-digital-guardian-frontend`

You still need to set:
- `GROQ_API_KEY` on the backend
- `GROQ_MODEL` on the backend if you want to override the default
- `ADMIN_EMAILS` on the backend if you want an admin account
- `REGISTRATION_MODE` and `REGISTRATION_INVITE_CODE` if you want to restrict public signups
- `ALLOWED_ORIGINS` on the backend
- `BACKEND_URL` on the frontend

## Tests

Run the automated integration tests with:

```bash
python -m unittest tests.test_app
```

## Current Limitations

This is a strong demo project, but still a prototype. Current limitations:

- passwords are not hashed yet
- authentication is basic
- authorization is not production-grade yet
- app blocking is simulated only
- Android integration is only a demo skeleton
- no automated test suite yet
- UI still uses manual student ID input in some flows

## Future Improvements

- password hashing with `bcrypt` or `passlib`
- JWT authentication
- role-based access protection
- better frontend UX
- real Android usage tracking
- real app blocking or parental control integration
- PostgreSQL-first production setup
- test coverage
- Docker support

## Why This Project Is Good For Learning

If you are a fresher, this project is useful because it demonstrates:
- API development with FastAPI
- frontend building with Streamlit
- database modeling with SQLAlchemy
- environment variable handling
- deployment preparation
- AI integration with fallback handling
- agent-style workflow thinking

## Screens You Can Show In GitHub Or Resume

- Registration
- Parent login
- Pair student flow
- Add usage screen
- Dashboard summary
- Alerts table
- AI chatbot response
- Daily report output

If you add screenshots later, this README will look even better on GitHub.

## Author Notes

This project is designed as a beginner-friendly GenAI / agentic AI learning project. It is especially suitable for:
- college mini projects
- portfolio demos
- internship discussions
- learning FastAPI + Streamlit integration

## License

Add your preferred license here, for example `MIT`.
