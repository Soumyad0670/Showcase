
import pytest
from app.models.portfolio import Portfolio

def test_routes_list(client):
    print("\n--- ROUTES ---")
    from app.main import app
    for r in app.routes:
        if hasattr(r, "path"):
            print(f"{r.methods} {r.path}")
    print("----------------")

def test_resume_upload_success(client):
    fake_file = ("resume.pdf", b"fake content", "application/pdf")
    response = client.post("/api/v1/resume/upload", files={"file": fake_file})
    print(f"\nResponse: {response.status_code} {response.text}")
    assert response.status_code == 202

def test_resume_upload_invalid(client):
    fake_file = ("resume.txt", b"fake content", "text/plain")
    response = client.post("/api/v1/resume/upload", files={"file": fake_file})
    print(f"\nResponse: {response.status_code} {response.text}")
    assert response.status_code == 400
