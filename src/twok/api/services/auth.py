import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional

from jose import JWTError, jwt

from twok.database import models, schemas
from twok.database.crud import DB


class Auth:
    ALGORITHM = "HS256"
    # token expires in 1 year
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, db: DB, secret_key: Optional[str] = None):
        self.db = db
        self._secret_key = secret_key
        if self._secret_key is None:
            self._secret_key = os.environ.get("JWT_SECRET_KEY")
        if self._secret_key is None:
            raise ValueError(
                """Provide a valid secret key by setting the `JWT_SECRET_KEY` environment variable.
                You can generate one with: openssl rand -hex 32"""
            )

    def verify_password(self, plain_password, password_hash):
        return self.pwd_context.verify(plain_password, password_hash)

    def password_hash(self, password):
        return self.pwd_context.hash(password)

    def authenticate_user(self, username: str, password: str):
        user = self.db.user.get(username)

        if not user:
            return False
        if not self.verify_password(password, user.password_hash):
            return False
        return user

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self._secret_key, algorithm=self.ALGORITHM)

        return encoded_jwt

    def register_user(self, user: models.User):
        db_user = self.db.user.get(user.username)
        if db_user:
            return None

        return self.db.user.create(
            username=user.username,
            password_hash=self.password_hash(user.plaintext_password),
        )

    def user(self, token: str):
        """
        Get user from token.
        We first decode the token to get the username, then we get the user from the database.
        This verifies that the token is valid and that the user exists. If the user does not exist,
        we return False.

        Args:
            token (str): The jwt token to decode.

        Returns:
            User: The user object if the token is valid and the user exists.
            False: If the token is invalid or the user does not exist.
        """
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return False
            token_data = schemas.TokenData(username=username)
        except JWTError:
            return False

        user = self.db.user.get(token_data.username)
        if user is None:
            return False

        return user
