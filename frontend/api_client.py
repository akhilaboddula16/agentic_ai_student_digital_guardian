import os
import requests
from dotenv import load_dotenv

load_dotenv()


def _get_streamlit_secret(name: str):
    try:
        import streamlit as st

        return st.secrets.get(name)
    except Exception:
        return None


BASE_URL = (
    _get_streamlit_secret("BACKEND_URL")
    or os.getenv("BACKEND_URL")
    or "http://127.0.0.1:8000"
).rstrip("/")

REQUEST_TIMEOUT_SECONDS = 60


def post(path, payload):
    response = requests.post(
        f"{BASE_URL}{path}",
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def get(path):
    response = requests.get(
        f"{BASE_URL}{path}",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()
