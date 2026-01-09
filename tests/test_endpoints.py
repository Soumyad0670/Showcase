import pytest
from app.models.portfolio import Portfolio

# Tests use 'client' and 'session' fixtures from conftest.py

def test_health_check(client):
    # DEBUG: Print all registered routes
    print("\n--- Registered Routes ---")
    for route in app.routes:
        if hasattr(route, "path"):
            print(f"{route.methods} {route.path}")
    print("-------------------------")

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_upload_resume_success(client):
    # Mocking a file upload
    fake_file = ("resume.pdf", b"fake pdf content", "application/pdf")
    
    response = client.post(
        "/api/v1/resume/upload",
        files={"file": fake_file}
    )
    
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "processing"

def test_upload_resume_invalid_format(client):
    fake_file = ("resume.txt", b"text content", "text/plain")
    
    response = client.post(
        "/api/v1/resume/upload",
        files={"file": fake_file}
    )
    
    # 400 Bad Request
    assert response.status_code == 400
    assert "Invalid file format" in response.json()["detail"]

def test_get_my_portfolios_empty(client, session):
    response = client.get("/api/v1/portfolios/me")
    assert response.status_code == 200
    assert response.json() == []

def test_get_my_portfolios_with_data(client, session):
    # Seed Data
    portfolio = Portfolio(
        job_id="job_123",
        user_id="test_user_123", # Matches mock user (conftest or dependency override?)
        full_name="Test User",
        content={"title": "My Portfolio"},
        is_published=False
    )
    session.add(portfolio)
    session.commit()

    response = client.get("/api/v1/portfolios/me")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["job_id"] == "job_123"

def test_get_specific_portfolio_access(client, session):
    # Seed Data owned by test user
    portfolio = Portfolio(
        job_id="job_own",
        user_id="test_user_123",
        full_name="Test User",
        content={"title": "Test"},
        is_published=False
    )
    session.add(portfolio)
    session.commit()

    response = client.get(f"/api/v1/portfolios/{portfolio.job_id}")
    assert response.status_code == 200
    assert response.json()["job_id"] == "job_own"

def test_get_portfolio_forbidden(client, session):
    # Seed Data owned by SOMEONE ELSE
    portfolio = Portfolio(
        job_id="job_other",
        user_id="other_user_999",
        full_name="Other User",
        content={"title": "Forbidden"},
        is_published=False
    )
    session.add(portfolio)
    session.commit()

    response = client.get(f"/api/v1/portfolios/{portfolio.job_id}")
    # Should expect 403 Forbidden
    assert response.status_code == 403

def test_publish_portfolio(client, session):
    portfolio = Portfolio(
        job_id="job_publish",
        user_id="test_user_123",
        full_name="Test User",
        content={"title": "Private"},
        is_published=False,
        theme_id="default"
    )
    session.add(portfolio)
    session.commit()

    # We need to send the correct schema for update
    update_payload = {"is_published": True, "deployed_url": "https://cool.com"}
    
    response = client.patch(
        f"/api/v1/portfolios/{portfolio.job_id}/publish",
        json=update_payload
    )
    
    assert response.status_code == 200
    assert response.json()["is_published"] == True
