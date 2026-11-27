import pytest
from werkzeug.security import check_password_hash

import app as app_module
from database import db


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def all_users():
    conn = db.get_db()
    try:
        return conn.execute("SELECT * FROM users").fetchall()
    finally:
        conn.close()


def post(client, name="Asha Rao", email="asha@example.com", password="password123", confirm=None):
    return client.post(
        "/register",
        data={
            "name": name,
            "email": email,
            "password": password,
            "confirm_password": password if confirm is None else confirm,
        },
    )


def test_get_renders_form_with_confirm_field(client):
    resp = client.get("/register")
    assert resp.status_code == 200
    assert b"Create your account" in resp.data
    assert b'name="confirm_password"' in resp.data
    assert b"Min. 8 characters" not in resp.data


def test_valid_registration_redirects_and_creates_user(client):
    resp = post(client)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")
    assert len(all_users()) == 1


def test_password_is_hashed(client):
    post(client)
    user = all_users()[0]
    assert user["password_hash"] != "password123"
    assert check_password_hash(user["password_hash"], "password123")


def test_short_password_is_allowed(client):
    resp = post(client, password="1234")
    assert resp.status_code == 302
    assert check_password_hash(all_users()[0]["password_hash"], "1234")


def test_email_trimmed_and_lowercased(client):
    post(client, email="  Asha@Example.COM  ")
    assert all_users()[0]["email"] == "asha@example.com"


def test_passwords_do_not_match(client):
    resp = post(client, password="abcd", confirm="abce")
    assert resp.status_code == 400
    assert b"Passwords do not match" in resp.data
    assert b'value="Asha Rao"' in resp.data
    assert b'value="asha@example.com"' in resp.data
    assert all_users() == []


def test_duplicate_email(client):
    post(client)
    resp = post(client, name="Other", email="ASHA@example.com")
    assert resp.status_code == 409
    assert b"Email already registered" in resp.data
    assert b'value="Other"' in resp.data
    assert len(all_users()) == 1


@pytest.mark.parametrize("field", ["name", "email", "password", "confirm_password"])
@pytest.mark.parametrize("value", ["", "   "])
def test_missing_or_blank_field(client, field, value):
    if field in ("password", "confirm_password") and value == "   ":
        pytest.skip("passwords are not stripped, so spaces count as a value")
    data = {
        "name": "Asha Rao",
        "email": "asha@example.com",
        "password": "1234",
        "confirm_password": "1234",
    }
    data[field] = value
    resp = client.post("/register", data=data)
    assert resp.status_code == 400
    assert b"All fields are required." in resp.data
    assert all_users() == []


def test_password_never_echoed_on_error(client):
    resp = post(client, password="secret-pass", confirm="different")
    assert b"secret-pass" not in resp.data
