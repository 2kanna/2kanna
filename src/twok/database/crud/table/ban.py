import sqlalchemy

from twok.database.crud.table import Table
from twok.database.models import Ban as BanModel


class Ban(Table):
    table = BanModel

    def __init__(self, session: sqlalchemy.orm.session.Session):
        super().__init__(session)

        self.main_column = BanModel.ban_id
