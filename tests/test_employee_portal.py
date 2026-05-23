from pathlib import Path
import sys

from fastapi.testclient import TestClient
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app as employee_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_database = tmp_path / "employees.db"
    monkeypatch.setattr(employee_app, "DATABASE_PATH", test_database)

    with TestClient(employee_app.app) as client:
        yield client


def test_smoke_pages_load(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Employee Data" in response.text

    response = client.get("/add")
    assert response.status_code == 200
    assert "Add a new employee" in response.text


def test_employee_crud_flow(client):
    response = client.post(
        "/add",
        data={
            "name": "Jack",
            "gender": "Male",
            "address": "US",
            "phone": "999945555",
            "salary": "890",
            "department": "IT",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Jack" in response.text
    assert "IT" in response.text

    response = client.get("/edit/1")
    assert response.status_code == 200
    assert "Edit employee" in response.text
    assert 'value="Jack"' in response.text

    response = client.post(
        "/edit/1",
        data={
            "name": "Jack Smith",
            "gender": "Male",
            "address": "US",
            "phone": "999945555",
            "salary": "1200",
            "department": "Engineering",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Jack Smith" in response.text
    assert "Engineering" in response.text
    assert "$1200.0" in response.text

    response = client.post(
        "/delete",
        data={"emp_id": "1"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Jack Smith" not in response.text


def test_missing_employee_returns_404(client):
    response = client.get("/edit/999")

    assert response.status_code == 404
