from .conftest import login_as


def test_dashboard_requires_auth(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_create_game_and_make_move(client, app):
    login_as(client, "alice")
    response = client.post(
        "/games",
        data={"opponent_id": 2, "preferred_color": "white"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    game_url = response.headers["Location"]

    state_response = client.get(f"{game_url}/state")
    payload = state_response.get_json()
    assert payload["changed"] is True
    version = payload["state"]["version"]

    move_response = client.post(
        f"{game_url}/moves",
        json={"from": "e2", "to": "e4", "expected_version": version},
    )
    assert move_response.status_code == 201
    body = move_response.get_json()
    assert body["state"]["turn"] == "black"
    assert body["state"]["moves"][0]["san"] == "e4"
