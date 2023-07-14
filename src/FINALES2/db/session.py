import pathlib
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from FINALES2.logging.logger import loggerConfig

DIRPATH_THIS = pathlib.Path(__file__).parent.resolve()
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DIRPATH_THIS}/sql_app.db"


logger_obj = loggerConfig()
logger = logger_obj.get_logger()


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False},
)
# connect_args articular connection in a thread which is not the one in which it was
# created

# Then, we are creating a SessionLocal.
# Once we create an instance of the SessionLocal class, this instance will be the actual
# database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        print("boomSauce")
        logger.info("A")
        logger.warning("B")
        logger.debug("C")
        db.close()
