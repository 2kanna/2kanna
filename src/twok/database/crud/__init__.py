import logging
from typing import Optional

import sqlalchemy
from sqlalchemy.sql.elements import UnaryExpression

from twok.database.models import (
    Board,
    Post,
    User,
)

from twok.database.crud.table.ban import Ban as BanCRUD
from twok.database.crud.table.board import Board as BoardCRUD
from twok.database.crud.table.file import File as FileCRUD
from twok.database.crud.table.post import Post as PostCRUD
from twok.database.crud.table.requester import Requester as RequesterCRUD
from twok.database.crud.table.user import User as UserCRUD

logger = logging.getLogger(__name__)


class DB:
    def __init__(self, session: sqlalchemy.orm.session.Session):
        self._session = session

        self.ban = BanCRUD(self._session)
        self.board = BoardCRUD(self._session)
        self.file = FileCRUD(self._session)
        self.post = PostCRUD(self._session)
        self.requester = RequesterCRUD(self._session)
        self.user = UserCRUD(self._session)

    def api_get(
        self,
        table,
        filter=[],
        order_by: Optional[UnaryExpression] = None,
        skip=0,
        limit=20,
    ):
        """Used within the API to get pagination list of entities

        Args:
            table (Table): Table object you want to query
            filter (list): List of filters to apply
            order_by (UnaryExpression, optional): Order by expression. Defaults to None.
            skip (int, optional): Number of entities to skip pass. Defaults to 0.
            limit (int, optional): Number of entities to return. Defaults to 20.

        Returns:
            list[entity]: List of entities
        """

        return (
            self._session.query(table)
            .filter(*filter)
            .order_by(order_by)
            .offset(skip)
            .limit(limit)
            .all()
        )
