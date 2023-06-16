import sqlalchemy

from twok.database.crud.table import Table
from twok.database.models import User as UserModel


class User(Table):
    table = UserModel

    def __init__(self, session: sqlalchemy.orm.session.Session):
        super().__init__(session)

        self.main_column = UserModel.username
