from urllib.parse import urlparse

import pytest
from werkzeug.security import generate_password_hash

import app as app_module
from database import db


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    db.seed_db()  # demo@spendly.com / demo123
    conn = db.get_db()
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Asha Rao", "asha@example.com", generate_password_hash("secret99")),
    )
    conn.commit()
    conn.close()
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def login(client, email="asha@example.com", password="secret99"):
    return client.post("/login", data={"email": email, "password": password})


def test_get_login_form(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b'action="/login"' in resp.data


def test_valid_login_sets_session_and_redirects(client):
    resp = login(client)
    assert resp.status_code == 302
    assert urlparse(resp.headers["Location"]).path == "/"
    with client.session_transaction() as sess:
        assert sess["user_id"]
        assert sess["user_name"] == "Asha Rao"


def test_demo_user_can_login(client):
    resp = login(client, "demo@spendly.com", "demo123")
    assert resp.status_code == 302
    assert urlparse(resp.headers["Location"]).path == "/"


def test_registered_user_can_login(client):
    client.post(
        "/register",
        data={"name": "New", "email": "new@example.com", "password": "1234", "confirm_password": "1234"},
    )
    resp = login(client, "new@example.com", "1234")
    assert resp.status_code == 302
    assert urlparse(resp.headers["Location"]).path == "/"


def test_email_case_and_whitespace_ignored(client):
    resp = login(client, "  ASHA@Example.com ")
    assert resp.status_code == 302


@pytest.mark.parametrize(
    "email,password",
    [("asha@example.com", "wrong"), ("nobody@example.com", "secret99")],
)
def test_bad_credentials(client, email, password):
    resp = login(client, email, password)
    assert resp.status_code == 401
    assert b"Invalid email or password" in resp.data
    with client.session_transaction() as sess:
        assert "user_id" not in sess


@pytest.mark.parametrize("email,password", [("", "secret99"), ("asha@example.com", "")])
def test_empty_fields(client, email, password):
    resp = login(client, email, password)
    assert resp.status_code == 400
    assert b"All fields are required." in resp.data


def test_failed_login_keeps_email_not_password(client):
    resp = login(client, "asha@example.com", "wrong-pass")
    assert b'value="asha@example.com"' in resp.data
    assert b"wrong-pass" not in resp.data


@pytest.mark.parametrize("path", ["/login", "/register"])
def test_logged_in_users_are_redirected(client, path):
    login(client)
    resp = client.get(path)
    assert resp.status_code == 302
    assert urlparse(resp.headers["Location"]).path == "/"


def test_navbar_reflects_session(client):
    out = client.get("/").data
    assert b"Sign in" in out and b"Get started" in out and b"Sign out" not in out
    login(client)
    inn = client.get("/").data
    assert b"Asha Rao" in inn and b"Sign out" in inn
    assert b"Get started" not in inn


def test_logout_clears_session(client):
    login(client)
    resp = client.get("/logout")
    assert resp.status_code == 302
    assert urlparse(resp.headers["Location"]).path == "/"
    with client.session_transaction() as sess:
        assert "user_id" not in sess
    assert b"Sign in" in client.get("/").data


def test_logout_when_logged_out(client):
    resp = client.get("/logout")
    assert resp.status_code == 302
    assert urlparse(resp.headers["Location"]).path == "/"
