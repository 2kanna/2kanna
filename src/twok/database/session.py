import os
import time
import logging
from typing import Optional

from sqlalchemy import create_engine, exc as sqlalchemy_exc
from sqlalchemy.orm import sessionmaker

from twok.database import Base
from twok.database.crud import DB

logger = logging.getLogger(__name__)


class Session:
    def __init__(self, db_url: Optional[str] = None):
        self._db_url = db_url or os.environ.get("DATABASE_URL")
        if not self._db_url:
            raise ValueError(
                "Provide a valid database URL by setting the `DATABASE_URL` environment variable."
            )
        self._db_connect()

    def __del__(self):
        logger.info("Closing database connection")
        self.close()

    def _db_connect(self):
        """Connect to the database and create all relevant tables if they don't exist"""
        if self._db_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        else:
            connect_args = {}

        self.__engine = create_engine(
            self._db_url,
            connect_args=connect_args,
            echo=False,
            pool_size=100,
            max_overflow=200,
        )

        connection_attempts = 0
        while True:
            try:
                connection_attempts += 1
                logger.info(
                    f"[{connection_attempts}] Attempting to connect to database"
                )

                # Attempt to connect and create all tables if they don't exist
                Base.metadata.create_all(self.__engine)

                logger.info(
                    f"[{connection_attempts}] Successfully connected to database"
                )
                break
            except sqlalchemy_exc.OperationalError as e:
                if connection_attempts == 300:
                    logger.error(
                        f"Failed to connect to database after {connection_attempts} attempts. Exiting."
                    )
                    raise e
                logger.warning("Failed to connect to base. Retrying in 5 seconds.")
                time.sleep(5)
        self.Session = sessionmaker(bind=self.__engine)

        self.create_default_data()

    def create_default_data(self):
        """Create default data if it doesn't exist"""
        session = self.Session()
        db = DB(session)

        if db.user.row_count() == 0:
            db.user.create(
                username="admin",
                password_hash="$2b$12$0fSMRdqMjZwESmCwR1z15u8VTpjS0SSZkpoTQ2mRibcO.7pxq6thG",
                user_role="admin",
            )

        if db.board.row_count() == 0:
            [db.board.create(name=name) for name in ["tech", "board2", "board3"]]

    def get_session(self):
        return self.Session()

    def close(self):
        self.__engine.dispose()
