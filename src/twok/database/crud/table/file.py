import sqlalchemy

from twok.database.crud.table import Table
from twok.database.models import File as FileModel


class File(Table):
    table = FileModel

    def __init__(self, session: sqlalchemy.orm.session.Session):
        super().__init__(session)

        self.main_column = FileModel.file_hash
