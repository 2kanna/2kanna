import sqlalchemy

from twok.api.config import Settings
from twok.database.crud.table import Table
from twok.database.models import Board as BoardModel


class Board(Table):
    table = BoardModel

    def __init__(self, session: sqlalchemy.orm.session.Session):
        super().__init__(session)

        self.main_column = BoardModel.name

    def all(self):
        return self._session.query(self.table).all()

    def page_count(self, board_name: str):
        board = self.get(board_name)

        if not board:
            return False

        if not board.posts:
            return 0

        post_count = len(board.posts)

        return (post_count // Settings().items_per_page) + 1
