from .conftest import login_as


def test_login_page_renders(client):
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Choose a seeded user" in response.data


def test_login_redirects_to_dashboard(client):
    response = login_as(client, "alice")
    assert response.status_code == 200
    assert b"Dashboard" in response.data
