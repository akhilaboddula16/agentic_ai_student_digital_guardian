import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DB_DIR = tempfile.TemporaryDirectory()
TEST_DB_PATH = Path(TEST_DB_DIR.name) / "bootstrap_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

from backend import security
from backend import database as database_module
from backend.database import Base, get_db
from backend.main import app
from backend.models.user_model import User
from backend.services import auth_service


class AppIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmpdir = TEST_DB_DIR
        cls.db_path = Path(cls._tmpdir.name) / "test.db"
        cls.engine = create_engine(
            f"sqlite:///{cls.db_path}",
            connect_args={"check_same_thread": False},
        )
        cls.SessionLocal = sessionmaker(bind=cls.engine, autoflush=False, autocommit=False)
        Base.metadata.create_all(bind=cls.engine)

        def override_get_db():
            db = cls.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

        cls.original_registration_mode = auth_service.REGISTRATION_MODE
        cls.original_registration_invite_code = auth_service.REGISTRATION_INVITE_CODE
        cls.original_auth_admin_emails = set(auth_service.ADMIN_EMAILS)
        cls.original_security_admin_emails = set(security.ADMIN_EMAILS)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        auth_service.REGISTRATION_MODE = cls.original_registration_mode
        auth_service.REGISTRATION_INVITE_CODE = cls.original_registration_invite_code
        auth_service.ADMIN_EMAILS = set(cls.original_auth_admin_emails)
        security.ADMIN_EMAILS = set(cls.original_security_admin_emails)
        Base.metadata.drop_all(bind=cls.engine)
        cls.engine.dispose()
        database_module.engine.dispose()

    def setUp(self):
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        auth_service.REGISTRATION_MODE = "open"
        auth_service.REGISTRATION_INVITE_CODE = ""
        auth_service.ADMIN_EMAILS = set()
        security.ADMIN_EMAILS = set()

    def _register(self, **payload):
        data = {
            "name": payload.get("name", "User"),
            "email": payload.get("email", "user@example.com"),
            "password": payload.get("password", "secret123"),
            "role": payload.get("role", "student"),
        }
        if "invite_code" in payload:
            data["invite_code"] = payload["invite_code"]
        return self.client.post("/auth/register", json=data)

    def _login(self, email: str, password: str):
        response = self.client.post("/auth/login", json={"email": email, "password": password})
        self.assertEqual(response.status_code, 200, response.text)
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_registration_hashes_password_and_pairing_protects_access(self):
        student = self._register(name="Student", email="student@example.com", role="student")
        parent = self._register(name="Parent", email="parent@example.com", role="parent")
        self.assertEqual(student.status_code, 200, student.text)
        self.assertEqual(parent.status_code, 200, parent.text)

        with self.SessionLocal() as db:
            stored_user = db.query(User).filter(User.email == "student@example.com").first()
            self.assertTrue(stored_user.password.startswith("scrypt$"))

        student_id = student.json()["id"]
        pair_code = student.json()["pair_code"]
        parent_headers = self._login("parent@example.com", "secret123")

        forbidden = self.client.get(f"/usage/student/{student_id}", headers=parent_headers)
        self.assertEqual(forbidden.status_code, 403, forbidden.text)

        pair_response = self.client.post("/auth/pair", json={"pair_code": pair_code}, headers=parent_headers)
        self.assertEqual(pair_response.status_code, 200, pair_response.text)

        usage_response = self.client.post(
            "/usage/add",
            json={
                "student_id": student_id,
                "app_name": "YouTube",
                "duration_minutes": 70,
                "limit_minutes": 60,
            },
            headers=parent_headers,
        )
        self.assertEqual(usage_response.status_code, 200, usage_response.text)

        summary_response = self.client.get(f"/usage/student/{student_id}/summary", headers=parent_headers)
        self.assertEqual(summary_response.status_code, 200, summary_response.text)
        self.assertEqual(summary_response.json()["YouTube"], 70)

    def test_protected_routes_require_authentication(self):
        response = self.client.get("/usage/student/1")
        self.assertEqual(response.status_code, 401, response.text)

    def test_admin_routes_work_for_whitelisted_admin(self):
        auth_service.ADMIN_EMAILS = {"admin@example.com"}
        security.ADMIN_EMAILS = {"admin@example.com"}

        admin_register = self._register(name="Admin", email="admin@example.com", role="parent")
        user_register = self._register(name="Student", email="student@example.com", role="student")
        self.assertEqual(admin_register.status_code, 200, admin_register.text)
        self.assertEqual(user_register.status_code, 200, user_register.text)

        admin_headers = self._login("admin@example.com", "secret123")
        admin_users = self.client.get("/admin/users", headers=admin_headers)
        self.assertEqual(admin_users.status_code, 200, admin_users.text)
        self.assertEqual(admin_users.json()["users"][0]["role"], "student")

        student_id = user_register.json()["id"]
        reset_response = self.client.delete(f"/admin/students/{student_id}/data", headers=admin_headers)
        self.assertEqual(reset_response.status_code, 200, reset_response.text)

    def test_invite_only_registration_requires_code(self):
        auth_service.REGISTRATION_MODE = "invite_only"
        auth_service.REGISTRATION_INVITE_CODE = "JOIN123"

        denied = self._register(email="locked@example.com", invite_code=None)
        self.assertEqual(denied.status_code, 400, denied.text)

        allowed = self._register(email="open@example.com", invite_code="JOIN123")
        self.assertEqual(allowed.status_code, 200, allowed.text)


if __name__ == "__main__":
    unittest.main()
