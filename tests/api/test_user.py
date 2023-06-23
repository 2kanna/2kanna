def test_create_user(client):
    with client as c:
        response = c.post(
            "/user",
            json={
                "username": "username",
                "plaintext_password": "password",
            },
        )

    assert response.status_code == 201

    assert "jwt" in response.json()
    assert "access_token" in response.json()["jwt"]
    assert response.json()["user"] == {
        "username": "username",
        "user_id": 2,
        "user_role": "none",
    }


def test_create_user_duplicate(create_user, client):
    with client as c:
        response = c.post(
            "/user",
            json={
                "username": "username",
                "plaintext_password": "password",
            },
        )
    assert response.status_code == 409
    assert response.json() == {"detail": "User already registered"}


def test_options_create_user(client):
    response = client.options("/user")
    assert response.status_code == 200
    assert response.headers == {
        "access-control-allow-origin": "*",
        "access-control-allow-methods": "OPTIONS, POST",
        "access-control-allow-headers": "accept, Content-Type, Authorization",
        "content-length": "0",
    }


def test_login(create_user, client):
    with client as c:
        response = c.post(
            "/user/token",
            data={
                "grant_type": "password",
                "username": "username",
                "password": "password",
            },
        )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(create_user, client):
    with client as c:
        response = c.post(
            "/user/token",
            data={
                "grant_type": "password",
                "username": "username",
                "password": "invalid_password",
            },
        )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


def test_login_nonexistent(client):
    with client as c:
        response = c.post(
            "/user/token",
            data={
                "grant_type": "password",
                "username": "username",
                "password": "password",
            },
        )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


def test_read_users_me(create_token, client):
    with client as c:
        response = c.get(
            "/user/me", headers={"Authorization": f"Bearer {create_token}"}
        )

    assert response.status_code == 200
    assert response.json() == {
        "username": "username",
        "user_id": 2,
        "user_role": "none",
    }


def test_read_users_me_no_token(client):
    with client as c:
        response = c.get("/user/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    assert response.headers["www-authenticate"] == "Bearer"


def test_read_users_me_invalid_token(client):
    with client as c:
        response = c.get("/user/me", headers={"Authorization": "Bearer invalid_token"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    assert response.headers["www-authenticate"] == "Bearer"


def test_options_read_users_me(client):
    response = client.options("/user/me")
    assert response.status_code == 200
    assert response.headers == {
        "access-control-allow-origin": "*",
        "access-control-allow-methods": "GET, OPTIONS",
        "access-control-allow-headers": "accept, Authorization",
        "content-length": "0",
    }


def test_delete_user(create_user, create_admin_token, client):
    with client as c:
        response = c.delete(
            "/user/2", headers={"Authorization": f"Bearer {create_admin_token}"}
        )

    assert response.status_code == 204
    assert response.text == ""


def test_delete_user_nonexistent(create_admin_token, client):
    with client as c:
        response = c.delete(
            "/user/2", headers={"Authorization": f"Bearer {create_admin_token}"}
        )

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_read_users_posts(create_admin_token, create_user_post, client):
    with client as c:
        response = c.get(
            "/user/2/posts", headers={"Authorization": f"Bearer {create_admin_token}"}
        )

    assert response.status_code == 200

    assert len(response.json()) == 1
    assert response.json()[0]["post_id"] == 1
    assert response.json()[0]["title"] == "Test Message Title"
    assert response.json()[0]["message"] == "Test Message"
    assert response.json()[0]["board"]["name"] == "board"


def test_ban_user(create_admin_token, create_requester_post, client):
    with client as c:
        response = c.post(
            "/user/ban",
            headers={"Authorization": f"Bearer {create_admin_token}"},
            json={"reason": "string", "post": {"post_id": 1}},
        )

    assert response.status_code == 204
    assert response.text == ""


def test_unban_user(create_admin_token, create_ban, client):
    with client as c:
        response = c.delete(
            "/user/ban/1",
            headers={"Authorization": f"Bearer {create_admin_token}"},
        )

    assert response.status_code == 204
    assert response.text == ""


def test_read_bans(create_admin_token, create_ban, client):
    with client as c:
        response = c.get(
            "/user/bans",
            headers={"Authorization": f"Bearer {create_admin_token}"},
        )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["ban_id"] == 1
    assert response.json()[0]["reason"] == "test ban"


def test_reset_password(create_admin_token, client):
    with client as c:
        response = c.post(
            "/user/reset_password",
            headers={"Authorization": f"Bearer {create_admin_token}"},
            json={"plaintext_password": "newpassword"},
        )

    breakpoint()

    assert response.status_code == 204
    assert response.text == ""
