from fastapi.testclient import TestClient


def test_get_post_empty(client):
    with client as c:
        response = c.get(
            "/post/1",
        )
    assert response.status_code == 404

    assert response.json() == {"detail": "Post not found"}


def test_get_posts(create_post, client):
    with client as c:
        response = c.get(
            "/post/1",
        )
    assert response.status_code == 200

    assert response.json()["post_id"] == 1
    assert response.json()["board"]["name"] == "board"


def test_create_post(create_board, client):
    with client as c:
        response = c.post(
            "/post",
            json={
                "title": "title",
                "message": "content",
                "board_name": "board",
            },
        )
    assert response.status_code == 201

    assert response.json()["post_id"] == 1
    assert response.json()["title"] == "title"
    assert response.json()["message"] == "content"
    assert response.json()["board"]["name"] == "board"


def test_create_post_with_file(create_board, create_file_no_post, client):
    with client as c:
        response = c.post(
            "/post",
            json={
                "title": "title",
                "message": "content",
                "board_name": "board",
                "file_id": create_file_no_post.file_id,
            },
        )
    assert response.status_code == 201

    assert response.json()["post_id"] == 1
    assert response.json()["title"] == "title"
    assert response.json()["message"] == "content"
    assert response.json()["board"]["name"] == "board"


def test_create_post_with_file_not_found(create_board, client):
    with client as c:
        response = c.post(
            "/post",
            json={
                "title": "title",
                "message": "content",
                "board_name": "board",
                "file_id": 1,
            },
        )
    assert response.status_code == 404

    assert response.json() == {"detail": "File not found"}


def test_delete_post(create_post, create_admin_token, client):
    headers = {"Authorization": f"Bearer {create_admin_token}"}

    with client as c:
        response = c.delete("/post/1", headers=headers)

    assert response.status_code == 204

    assert response.text == ""


def test_create_post_invalid_board(client):
    with client as c:
        response = c.post(
            "/post",
            json={
                "title": "title",
                "message": "content",
                "board_name": "board",
            },
        )
    assert response.status_code == 404

    assert response.json() == {"detail": "Board not found"}


def test_upload_file(create_post, client: TestClient):
    with open("tests/fixtures/the_metamorphosis.jpg", "rb") as f, client as c:
        response = c.post(
            "/post/upload",
            files={"file": ("the_metamorphosis.jpg", f, "image/jpeg")},
            data={"post_id": 1},
        )

    assert response.status_code == 201

    assert response.json() == {
        "file_id": 1,
        "file_name": "the_metamorphosis.jpg",
        "file_hash": "aff4996afe18fa33760ea1eb463f6fa71f8b01f251ef7e969e9c3b21c7a5cbc8",
        "content_type": "image/jpeg",
        "post_id": 1,
    }


def test_delete_file(create_admin_token, create_file, client: TestClient):
    with client as c:
        response = c.delete(
            "/post/upload/1", headers={"Authorization": f"Bearer {create_admin_token}"}
        )

    assert response.status_code == 204

    assert response.text == ""


def test_upload_non_existent_post(client: TestClient):
    with open("tests/fixtures/the_metamorphosis.jpg", "rb") as f, client as c:
        response = c.post(
            "/post/upload",
            files={"file": ("the_metamorphosis.jpg", f, "image/jpeg")},
            data={"post_id": 2},
        )

    assert response.status_code == 404

    assert response.json() == {"detail": "Post not found"}


def test_upload_file_already_exists(create_file, client: TestClient):
    with open("tests/fixtures/the_metamorphosis.jpg", "rb") as f, client as c:
        response = c.post(
            "/post/upload",
            files={"file": ("the_metamorphosis.jpg", f, "image/jpeg")},
            data={"post_id": 1},
        )

    assert response.status_code == 409

    assert response.json() == {"detail": "File already exists"}
