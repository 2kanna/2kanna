import asyncio
import html
from datetime import datetime
from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    Form,
    UploadFile,
    Response,
)
from sse_starlette.sse import EventSourceResponse

from twok import files
from twok.api import dependencies
from twok.database import schemas, models

post_router = APIRouter(
    prefix="/post",
    tags=["Post"],
    responses={404: {"description": "Not found"}},
)


@post_router.get("/{post_id}", response_model=schemas.Post)
def read_post(post: dependencies.root_post):
    return post


@post_router.get("/stream/{post_id}", response_model=schemas.Post)
async def stream_data(
    json_post: dependencies.root_json_post,
    background_tasks: BackgroundTasks,
    db: dependencies.database,
):
    async def event_generator():
        yield dict(event="init_post", data=json_post)

        latest_reply = (
            json_post.get("children")[-1].get("post_id")
            if json_post.get("children")
            else json_post.get("post_id")
        )

        while True:
            # [TODO] refactor this so we don't have to poll the database every second
            replies = db.api_get(
                models.Post,
                filter=[
                    models.Post.parent_id == json_post.get("post_id"),
                    models.Post.post_id > latest_reply,
                ],
                limit=50,
            )

            # Yield the new replies to the client
            if replies:
                latest_reply = replies[-1].post_id

                json_replies = []

                for reply in replies:
                    json_reply = dependencies.create_json_post(reply)
                    json_replies.append(json_reply)

                yield dict(
                    event="update_post",
                    data=json_replies,
                )

            # Wait for 1 second before executing the query again
            await asyncio.sleep(1)

    # Start the background task to execute the query periodically
    background_tasks.add_task(event_generator)

    # Return the EventSourceResponse to the client
    return EventSourceResponse(event_generator())


@post_router.options("", response_model=schemas.Post)
def options_create_post():
    return Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS, POST",
            "Access-Control-Allow-Headers": "accept, Authorization, Content-Type",
        }
    )


@post_router.delete("/{post_id}", status_code=204)
def delete_post(
    post: dependencies.post,
    db: dependencies.database,
    current_user_is_admin: dependencies.current_user_is_admin = None,
):
    db.post.delete(post)

    return None


@post_router.post("", response_model=schemas.Post, status_code=201)
def create_post(
    post: schemas.PostCreate,
    db: dependencies.database,
    post_prechecks: dependencies.post_prechecks,
    optional_current_user: dependencies.optional_current_user = None,
):
    db_board = db.board.get(filter=[models.Board.name == post.board_name])
    if not db_board:
        raise HTTPException(status_code=404, detail="Board not found")

    post_messaged_escaped = html.escape(post.message)

    user_id = optional_current_user.user_id if optional_current_user else None

    db_post = db.post.create(
        title=post.title,
        message=post_messaged_escaped,
        date=str(datetime.now()),
        board_id=db_board.board_id,
        parent_id=post.parent_id,
        user_id=user_id,
        requester_id=post_prechecks.requester_id,
    )

    if post.file_id:
        db_file = db.file.get(filter=[models.File.file_id == post.file_id])
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")

        db.file.update(db_file, post_id=db_post.post_id)

    return db_post


@post_router.post("/upload", response_model=schemas.FileBase, status_code=201)
async def upload_file(
    db: dependencies.database,
    file: UploadFile,
    post_id: Annotated[Optional[int], Form()] = None,
):
    file_hash = await files.save_upload_file(file)

    if post_id:
        db_post = db.post.get(filter=[models.Post.post_id == post_id])
        if not db_post:
            raise HTTPException(status_code=404, detail="Post not found")

    db_file = db.file.create(
        filter=None,
        file_name=file.filename,
        file_hash=file_hash,
        content_type=file.content_type,
        post_id=post_id,
    )

    if not db_file:
        raise HTTPException(status_code=409, detail="File already exists")

    return db_file


@post_router.delete("/upload/{file_id}", status_code=204)
def delete_file(
    file: dependencies.file,
    db: dependencies.database,
    current_user_is_admin: dependencies.current_user_is_admin = None,
):
    files.delete_file(file, db)

    return None
