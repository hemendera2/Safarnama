import json


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


def test_auth_register_and_login(client):
    # Register
    reg_data = {
        "email": "testuser@example.com",
        "password": "testpassword",
        "full_name": "Test User",
    }
    response = client.post(
        "/api/v1/auth/register",
        data=json.dumps(reg_data),
        content_type="application/json",
    )
    assert response.status_code == 201

    # Login
    login_data = {"email": "testuser@example.com", "password": "testpassword"}
    response = client.post(
        "/api/v1/auth/login",
        data=json.dumps(login_data),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert "access_token" in response.get_json()


def test_get_places_empty(client):
    response = client.get("/api/v1/places/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["items"] == []
    assert data["total"] == 0
