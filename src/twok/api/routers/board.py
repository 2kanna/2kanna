from fastapi import APIRouter, HTTPException

from twok.api import dependencies
from twok.database import schemas

board_router = APIRouter(
    prefix="/board",
    tags=["Board"],
    responses={404: {"description": "Not found"}},
)


@board_router.get("", response_model=list[schemas.BoardBase])
def read_boards(db: dependencies.database):
    return db.board.all()


@board_router.get("/{board_name}/posts", response_model=list[schemas.Post])
def read_board(posts: dependencies.posts):
    return posts


@board_router.get("/{board_name}/posts/pagecount", response_model=int)
def read_board_page_count(page_count: dependencies.page_count):
    return page_count


@board_router.post("", response_model=schemas.Board, status_code=201)
def create_board(board: schemas.BoardCreate, db: dependencies.database):
    db_board = db.board.create(
        filter=None,
        name=board.name,
    )

    if db_board:
        return db_board
    else:
        raise HTTPException(status_code=409, detail="Board already exists")
