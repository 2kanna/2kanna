import sqlalchemy

from twok.database.crud.table import Table
from twok.database.models import Requester as RequesterModel


class Requester(Table):
    table = RequesterModel

    def __init__(self, session: sqlalchemy.orm.session.Session):
        super().__init__(session)

        self.main_column = RequesterModel.ip_address
