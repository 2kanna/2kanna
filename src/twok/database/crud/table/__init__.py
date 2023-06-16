import logging
import sqlalchemy
from typing import Optional

logger = logging.getLogger(__name__)


class Table:
    table: sqlalchemy.Table
    main_column: sqlalchemy.Column

    def __init__(self, session: sqlalchemy.orm.session.Session):
        self._session = session

    def get(
        self,
        name: Optional[str] = None,
        table: Optional[sqlalchemy.Table] = None,
        filter: Optional[list] = False,
    ):
        """Get an entity if one doesn't exist with the given name (or by given filter)
        Args:
            filter (bool, optional): Optional `where` list . Defaults to False which is filter by `this.main_column`.

        Returns:
            (object, None): pre-existing entity object, or `None` if no entity is found
        """
        if not table:
            table = self.table

        if not filter:
            filter = [self.main_column == name]

        entity = self._session.query(table).filter(*filter).first()

        if entity:
            return entity

    def row_count(self, table: Optional[sqlalchemy.Table] = None):
        """Get the number of rows in the table

        Args:
            table (sqlalchemy.Table, optional): Table to count. Defaults to None.

        Returns:
            int: Number of rows in the table
        """
        if not table:
            table = self.table

        return self._session.query(table).count()

    def create(self, filter=None, **kwargs):
        """Create an entity
        Args:
            **kwargs: Entity attributes

        n.b. this functions means no entity can have a column named `filter`

        Returns:
            (object, None): newly created entity object.
        """
        # We are able to blindly create an entity if `filter=False`
        # if `filter` is `None` we need to check if an entity already exists using it's main column
        if filter is not False:
            if not filter:
                filter = [self.main_column == kwargs[self.main_column.name]]

            if self.get(filter=filter):
                return False

        entity = self.table(**kwargs)
        self._session.add(entity)
        self._session.commit()

        return entity

    def update(self, entity, **kwargs: dict) -> object:
        """Update an entity

        Args:
            entity (entity): Entity to update
        """

        for key, value in kwargs.items():
            setattr(entity, key, value)

        self._session.commit()

        return entity

    def delete(self, entity):
        """Delete an entity

        Args:
            entity (entity): Entity to delete
        """
        self._session.delete(entity)
        self._session.commit()
