def test_create_board(client):
    with client as c:
        response = c.post(
            "/board",
            json={
                "name": "board",
            },
        )
    assert response.status_code == 201

    assert response.json() == {"name": "board", "board_id": 4, "posts": []}


def test_create_board_duplicate(create_board, client):
    with client as c:
        response = c.post(
            "/board",
            json={
                "name": "board",
            },
        )

    assert response.status_code == 409
    assert response.json() == {"detail": "Board already exists"}


def test_get_boards_default(client):
    with client as c:
        response = c.get(
            "/board",
        )
    assert response.status_code == 200

    assert response.json() == [{"name": "tech"}, {"name": "board2"}, {"name": "board3"}]


def test_get_boards(create_board, client):
    with client as c:
        response = c.get(
            "/board",
        )
    assert response.status_code == 200

    assert response.json() == [
        {"name": "tech"},
        {"name": "board2"},
        {"name": "board3"},
        {"name": "board"},
    ]


def test_get_posts_empty(create_board, client):
    with client as c:
        response = c.get(
            "/board/board/posts",
        )
    assert response.status_code == 200

    assert response.json() == []


def test_get_posts(create_post, client):
    with client as c:
        response = c.get(
            "/board/board/posts",
        )
    assert response.status_code == 200

    assert len(response.json()) == 1
    assert response.json()[0]["post_id"] == 1
    assert response.json()[0]["board"]["name"] == "board"


def test_get_posts_page_count_no_board(client):
    with client as c:
        response = c.get(
            "/board/board/posts/pagecount",
        )
    assert response.status_code == 404

    assert response.json() == {"detail": "Board not found"}


def test_get_posts_page_count_empty(create_board, client):
    with client as c:
        response = c.get(
            "/board/board/posts/pagecount",
        )
    assert response.status_code == 200

    assert response.json() == 0


def test_get_posts_page_count(create_post, client):
    with client as c:
        response = c.get(
            "/board/board/posts/pagecount",
        )
    assert response.status_code == 200

    assert response.json() == 1
