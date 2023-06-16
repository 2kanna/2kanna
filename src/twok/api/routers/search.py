from fastapi import APIRouter

from twok.api import dependencies
from twok.database import schemas

search_router = APIRouter(
    prefix="/search",
    tags=["Search"],
    responses={404: {"description": "Not found"}},
)


@search_router.get(
    "/board/{board_name}/post/{query}", response_model=list[schemas.Post]
)
def search_post_by_board(posts: dependencies.search_posts):
    return posts


@search_router.get("/post/{query}", response_model=list[schemas.Post])
def search_post(posts: dependencies.search_posts):
    return posts


# @search_router.get("/board/{query}", response_model=list[schemas.Board])
# def search_post(query: str, db: dependencies.database):
#     db_results = db.board.search(query)

#     return db_results
