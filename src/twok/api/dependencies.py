import hashlib
from datetime import datetime
from typing import Annotated, Dict, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer

from twok.api.config import Settings
from twok.api.services.auth import Auth
from twok.database.crud import DB
from twok.database import schemas, models


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/token")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/token", auto_error=False)


def _db(request: Request):
    db_session = request.app.state.db_pool.get_session()

    db = DB(session=db_session)
    try:
        yield db
    finally:
        db_session.close()
        del db


def _settings() -> Settings:
    return Settings()


def _pagination_parameters(page: int = 1, settings: Settings = Depends(_settings)):
    # Can you use a dataclass here, does it make sense to?
    skip = (page - 1) * settings.items_per_page

    return {"skip": skip, "limit": settings.items_per_page}


def _page_count(board_name: str, db: DB = Depends(_db)):
    page_count = db.board.page_count(board_name)

    if page_count is False:
        # specifically check for `is False` because page_count can be 0
        raise HTTPException(status_code=404, detail="Board not found")

    return page_count


def _auth(db: DB = Depends(_db)):
    auth = Auth(db)
    try:
        yield auth
    finally:
        del auth


async def _current_user(
    auth: Auth = Depends(_auth), token: str = Depends(oauth2_scheme)
):
    user = auth.user(token)
    if user:
        return user

    raise HTTPException(
        status_code=401,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def _optional_current_user(
    auth: Auth = Depends(_auth), token: Optional[str] = Depends(optional_oauth2_scheme)
):
    if token:
        user = auth.user(token)
        if user:
            return user

    return None


async def _current_user_is_admin(
    current_user: schemas.User = Depends(_current_user),
):
    if not current_user.user_role == "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    return current_user


def _user(user_id: int, db: DB = Depends(_db)):
    db_user = db.user.get(filter=[models.User.user_id == user_id])

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


def _can_view_user_profile(
    current_user: schemas.User = Depends(_current_user),
    user: schemas.User = Depends(_user),
):
    if current_user.user_role == "admin":
        return True

    if current_user.user_id == user.user_id:
        return True

    return False


def _file(file_id: int, db: DB = Depends(_db)):
    db_file = db.file.get(filter=[models.File.file_id == file_id])

    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")

    return db_file


def _post(post_id: int, db: DB = Depends(_db)):
    db_post = db.post.get(filter=[models.Post.post_id == post_id])

    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return db_post


def _root_post(db_post: models.Post = Depends(_post), db: DB = Depends(_db)):
    if db_post.parent_id:
        db_post = db.post.get(filter=[models.Post.post_id == db_post.parent_id])

    return db_post


def _root_json_post(db_post: models.Post = Depends(_root_post)):
    return create_json_post(db_post)


def create_json_post(db_post):
    encoder_kwargs = dict(
        exclude={"user_id", "requester_id"},
        exclude_unset=True,
        exclude_none=True,
    )

    json_post = jsonable_encoder(db_post, **encoder_kwargs)
    if db_post.file:
        json_file = jsonable_encoder(db_post.file, **encoder_kwargs)
        json_post["file"] = json_file

    children = []
    for child in db_post.children:
        child_dict = jsonable_encoder(child, **encoder_kwargs)
        if child.file:
            child_file_dict = jsonable_encoder(child.file, **encoder_kwargs)
            child_dict["file"] = child_file_dict
        children.append(child_dict)

    json_post["children"] = children

    return json_post


def _posts(
    board_name: str,
    pagination: Dict = Depends(_pagination_parameters),
    db: DB = Depends(_db),
):
    board = db.board.get(filter=[models.Board.name == board_name])
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")

    filter = [
        models.Post.board_id == board.board_id,
        models.Post.parent_id == None,  # noqa: E711
    ]

    db_posts = db.api_get(
        table=models.Post,
        filter=filter,
        order_by=models.Post.latest_reply_date.desc(),
        skip=pagination["skip"],
        limit=pagination["limit"],
    )

    for post in db_posts:
        # get 3 replies for each post ordered by latest_reply_date
        post.children = db.post.get(
            filter=[models.Post.parent_id == post.post_id],
            order_by=models.Post.latest_reply_date.desc(),
            limit=3,
        )

    if db_posts is None:
        raise HTTPException(status_code=404, detail="Posts not found")

    return db_posts


def _user_posts(
    user_id: int,
    pagination: Dict = Depends(_pagination_parameters),
    db: DB = Depends(_db),
):
    db_posts = db.api_get(
        table=models.Post,
        filter=[models.Post.user_id == user_id],
        order_by=models.Post.latest_reply_date.desc(),
        skip=pagination["skip"],
        limit=pagination["limit"],
    )

    if db_posts is None:
        raise HTTPException(status_code=404, detail="Posts not found")

    return db_posts


def _board(board_name: str, db: DB = Depends(_db)):
    db_board = db.board.get(filter=[models.Board.name == board_name])

    if db_board is None:
        raise HTTPException(status_code=404, detail="Board not found")

    return db_board


def _search_posts(
    query: str,
    board_name: Optional[str] = None,
    pagination: Dict = Depends(_pagination_parameters),
    db: DB = Depends(_db),
):
    db_results = db.post.search(
        query=query,
        board_name=board_name,
        skip=pagination["skip"],
        limit=pagination["limit"],
    )

    if db_results is None:
        raise HTTPException(status_code=404, detail="Posts not found")

    return db_results


# def _banned(
#     request: Request,
#     db: DB = Depends(_db),
# ):
#     requester_ip_addr = request.client.host
#     db_ban = db.ban.get(filter=[models.Ban.ip_address == requester_ip_addr])

#     if db_ban:
#         raise HTTPException(status_code=403, detail=f"Banned: {db_ban.reason}")

#     return False


def _post_prechecks(
    request: Request,
    db: DB = Depends(_db),
    settings: Settings = Depends(_settings),
):
    requester_ip_addr = request.client.host

    db_requester = db.requester.get(
        filter=[models.Requester.ip_address == requester_ip_addr]
    )

    try:
        if db_requester.bans:
            raise HTTPException(
                status_code=403, detail=f"Banned: {db_requester.bans[0].reason}"
            )

        # Retrieve the last post time from the database
        last_post_time: str = db_requester.last_post_time
        current_time: datetime = datetime.now()

        # Calculate the time difference between the current time and the last post time
        # and represent it as a timedelta object
        time_difference = current_time - datetime.strptime(
            last_post_time, "%Y-%m-%d %H:%M:%S.%f"
        )

        # If the time difference is less than the limit, return False to indicate that the post is not allowed
        if time_difference < settings.post_time_limit:
            raise HTTPException(status_code=429, detail="Posting too fast")

        db.requester.update(db_requester, last_post_time=current_time)
    except AttributeError:
        # Trying to access `db_requester.bans``
        # If the requester IP address doesn't exist in the database, create a new entry
        db_requester = db.requester.create(
            filter=None,
            ip_address=requester_ip_addr,
            last_post_time=datetime.now(),
        )

    # Return db_requester to indicate that the post is allowed
    return db_requester


def _ban(ban_id: int, db: DB = Depends(_db)):
    db_ban = db.ban.get(filter=[models.Ban.ban_id == ban_id])

    if db_ban is None:
        raise HTTPException(status_code=404, detail="Ban not found")

    return db_ban


def _fingerprint(request: Request):
    """
    create a "fingerprint" of the user, based of their:
        - IP address
        - user agent
        - language
    """
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    language = request.headers.get("accept-language")

    return hashlib.sha512(f"{ip_address}{user_agent}{language}".encode()).hexdigest()


auth = Annotated[Auth, Depends(_auth)]
ban = Annotated[models.Ban, Depends(_ban)]
current_user = Annotated[bool, Depends(_current_user)]
optional_current_user = Annotated[bool, Depends(_optional_current_user)]
current_user_is_admin = Annotated[bool, Depends(_current_user_is_admin)]
can_view_user_profile = Annotated[bool, Depends(_can_view_user_profile)]
database = Annotated[DB, Depends(_db)]
pagination_parameters = Annotated[dict, Depends(_pagination_parameters)]
fingerprint = Annotated[str, Depends(_fingerprint)]
file = Annotated[models.File, Depends(_file)]
page_count = Annotated[int, Depends(_page_count)]
post = Annotated[schemas.Post, Depends(_post)]
posts = Annotated[list[schemas.Post], Depends(_posts)]
board = Annotated[schemas.Board, Depends(_board)]
root_post = Annotated[schemas.Post, Depends(_root_post)]
root_json_post = Annotated[schemas.Post, Depends(_root_json_post)]
search_posts = Annotated[list[schemas.Post], Depends(_search_posts)]
post_prechecks = Annotated[bool, Depends(_post_prechecks)]
user = Annotated[schemas.User, Depends(_user)]
user_posts = Annotated[list[schemas.Post], Depends(_user_posts)]
