from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm

from twok.api import dependencies

from twok.database import schemas, models


user_router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={404: {"description": "Not found"}},
)


@user_router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: dependencies.current_user):
    return current_user


# preflight options req for /user/me
@user_router.options("/me", response_model=schemas.User)
async def options_user_me():
    return Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "accept, Authorization",
        }
    )


@user_router.get("/{user_id}/posts", response_model=list[schemas.Post])
async def read_users_posts(
    user: dependencies.user,
    db: dependencies.database,
    can_view_user_profile: dependencies.can_view_user_profile = None,
    user_posts: dependencies.user_posts = None,
):
    return user_posts


@user_router.post("/token", response_model=schemas.Token)
async def login(
    auth: dependencies.auth, form_data: OAuth2PasswordRequestForm = Depends()
):
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = auth.create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}


@user_router.post("", response_model=schemas.UserAndToken, status_code=201)
async def create_user(user: schemas.UserCreate, auth: dependencies.auth):
    # "registering" a user is more of a "crud" task. We will probably move that.
    # creating of the token still requires `auth`.
    db_user = auth.register_user(user)
    if db_user:
        access_token = auth.create_access_token(data={"sub": user.username})
        return {
            "user": db_user,
            "jwt": {"access_token": access_token, "token_type": "bearer"},
        }
    else:
        raise HTTPException(status_code=409, detail="User already registered")


@user_router.options("", response_model=schemas.User)
async def options_user():
    return Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS, POST",
            "Access-Control-Allow-Headers": "accept, Content-Type, Authorization",
        },
    )


@user_router.post("/ban", status_code=204)
def ban_user_requester(
    ban: schemas.BanCreate,
    db: dependencies.database,
    current_user_is_admin: dependencies.current_user_is_admin = None,
):
    """
    Posting as an authenticated user is optional.
    We want to ban the "user"/"requester"'s IP address.
    """

    db_post = db.post.get(filter=[models.Post.post_id == ban.post.post_id])

    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    if not db_post.requester:
        raise HTTPException(status_code=404, detail="Requester not found")

    db.ban.create(
        filter=False,
        requester_id=db_post.requester.requester_id,
        reason=ban.reason,
        date=datetime.now(),
        expiration=datetime.now() + timedelta(days=7),
    )

    return None


@user_router.delete("/ban/{ban_id}", status_code=204)
def unban_user_requester(
    ban: dependencies.ban,
    db: dependencies.database,
    current_user_is_admin: dependencies.current_user_is_admin = None,
):
    db.ban.delete(ban)

    return None


@user_router.get("/bans", response_model=list[schemas.Ban])
def get_bans(
    pagination: dependencies.pagination_parameters,
    db: dependencies.database,
    current_user_is_admin: dependencies.current_user_is_admin = None,
):
    # filter = [models.Post.board_id == board.board_id and models.Post.parent_id == None]
    # print("hi")
    # return None

    db_bans = db.api_get(
        table=models.Ban,
        # filter=filter,
        order_by=models.Ban.date.desc(),
        skip=pagination["skip"],
        limit=pagination["limit"],
    )

    if db_bans is None:
        raise HTTPException(status_code=404, detail="Bans not found")

    return db_bans


@user_router.delete("/{user_id}", status_code=204)
async def delete_user(
    user: dependencies.user,
    db: dependencies.database,
    current_user_is_admin: dependencies.current_user_is_admin = None,
):
    db.user.delete(user)

    return None


@user_router.post("/reset_password", status_code=204)
async def reset_password(
    new_password: schemas.UserResetPassword,
    current_user: dependencies.current_user,
    auth: dependencies.auth,
):
    auth.reset_password(current_user, new_password.plaintext_password)

    return None
