# tests/http/test_routes.py
# Flask test client; no real DB or network needed
import pytest
from app import db, Students

def test_index_returns_200(client):
    """GET / returns HTTP 200."""
    assert client.get("/").status_code == 200

def test_new_form_returns_200(client):
    """GET /new returns the student form."""
    assert client.get("/new").status_code == 200

def test_add_student_redirects(client):
    """POST /new with all fields gets 302."""
    r = client.post("/new", data={
        "name": "Alice Smith", "city": "Miami",
        "addr": "123 Main St", "pin": "33101",
        "phone": "305-555-1234"
    })
    assert r.status_code == 302

def test_student_appears_on_list(client):
    """Added student appears on home page."""
    client.post("/new", data={
        "name": "Bob Jones", "city": "Hialeah",
        "addr": "1 Oak Ave", "pin": "33012",
        "phone": "305-555-0001"
    })
    r = client.get("/", follow_redirects=True)
    assert b"Bob Jones" in r.data

@pytest.mark.parametrize("missing", ["name", "city", "addr"])
def test_required_fields(client, missing):
    """Each required field is rejected. pin and phone are optional."""
    data = {"name": "Alice", "city": "Miami", "addr": "1 St",
            "pin": "33101", "phone": "305-555-0000"}
    data[missing] = ""
    before = Students.query.count()
    r = client.post("/new", data=data)
    assert r.status_code == 200
    assert Students.query.count() == before

@pytest.mark.parametrize("flag", ["true", "false"])
def test_form_major_field(client, monkeypatch, flag):
    """Major input appears on /new only when ENABLE_MAJOR_FIELD is true."""
    monkeypatch.setenv("ENABLE_MAJOR_FIELD", flag)
    r = client.get("/new")
    shown = b'name="major"' in r.data
    assert shown == (flag == "true")

@pytest.mark.parametrize("flag", ["true", "false"])
def test_list_major_column(client, monkeypatch, flag):
    """Major column header appears on / only when ENABLE_MAJOR_FIELD is true."""
    monkeypatch.setenv("ENABLE_MAJOR_FIELD", flag)
    r = client.get("/")
    shown = b'<th>Major</th>' in r.data
    assert shown == (flag == "true")

@pytest.mark.parametrize("flag", ["true", "false"])
def test_post_major_field_persistence(client, monkeypatch, flag):
    """Major is stored when flag is true; ignored (None) when flag is false."""
    monkeypatch.setenv("ENABLE_MAJOR_FIELD", flag)
    name = f"Test Major {flag}"
    r = client.post("/new", data={
        "name": name,
        "city": "Miami",
        "addr": "123 Main St",
        "pin": "33101",
        "phone": "305-555-1234",
        "major": "Computer Science"
    }, follow_redirects=True)
    assert r.status_code == 200
    student = Students.query.filter_by(name=name).first()
    assert student is not None
    if flag == "true":
        assert student.major == "Computer Science"
    else:
        assert student.major is None
