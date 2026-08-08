from src.models import User, UserRole, db


def test_admin_dashboard_rbac(client, app):
    # 1. Anonymous Access
    response = client.get("/api/v1/analytics/dashboard")
    assert response.status_code == 401

    # 2. Traveler Access
    with app.app_context():
        traveler = User(email="traveler@safarnama.in", full_name="Traveler")
        traveler.set_password("pass123")
        traveler.role = UserRole.TRAVELER
        db.session.add(traveler)
        db.session.commit()

        login_res = client.post(
            "/api/v1/auth/login",
            json={"email": "traveler@safarnama.in", "password": "pass123"},
        )
        token = login_res.get_json()["access_token"]

        response = client.get(
            "/api/v1/analytics/dashboard", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403

    # 3. Admin Access
    with app.app_context():
        admin = User(email="admin@safarnama.in", full_name="Admin")
        admin.set_password("admin123")
        admin.role = UserRole.ADMIN
        db.session.add(admin)
        db.session.commit()

        login_res = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@safarnama.in", "password": "admin123"},
        )
        token = login_res.get_json()["access_token"]

        response = client.get(
            "/api/v1/analytics/dashboard", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
