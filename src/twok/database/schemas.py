"""pydantic models used in fastapi
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Requester(BaseModel):
    ip_address: str
    last_post_time: Optional[datetime] = None

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    plaintext_password: str


class User(UserBase):
    user_id: int
    user_role: str = "none"

    class Config:
        orm_mode = True


class UserAndToken(BaseModel):
    user: User
    jwt: "Token"

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class BoardBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class BoardCreate(BoardBase):
    pass


class PostBase(BaseModel):
    title: str = None
    message: str


class PostCreate(PostBase):
    board_name: str
    parent_id: Optional[int] = None
    file_id: Optional[int] = None


class Post(PostBase):
    post_id: int
    board: BoardBase
    date: str
    file: Optional["FileBase"] = None
    parent_id: Optional[int] = None
    children: list["Post"] = []
    latest_reply_date: Optional[str] = None

    class Config:
        orm_mode = True


class Posts(BaseModel):
    posts: list[Post]

    class Config:
        orm_mode = True


class FileBase(BaseModel):
    file_id: int
    file_name: str
    file_hash: str
    content_type: str
    post_id: Optional[int] = None

    class Config:
        orm_mode = True


class Board(BoardBase):
    board_id: int
    posts: list[Post]

    class Config:
        orm_mode = True


class SearchListResponse(BaseModel):
    posts: list[Optional[Post]]
    boards: list[Optional[Board]]


# class BanBase(BaseModel):
#     ban_id = int
#     ip_address = str
#     reason = str
#     date = str
#     expiration = str
#     active = int

#     class Config:
#         orm_mode = True


# class BanCreate(BanBase):
#     hello = str


class PostBan(BaseModel):
    post_id: int


class BanBase(BaseModel):
    reason: str

    class Config:
        orm_mode = True


class BanCreate(BanBase):
    post: PostBan


class Ban(BanBase):
    ban_id: int
    requester: Requester
    date: datetime
    expiration: datetime
    active: bool

    class Config:
        orm_mode = True


class BanDelete(BaseModel):
    ban_id: int


class HealthCheckResponse(BaseModel):
    status: str
    time: datetime


Post.update_forward_refs()
UserAndToken.update_forward_refs()
Requester.update_forward_refs()
