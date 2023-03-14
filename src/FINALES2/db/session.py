from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# from core.config import settings


SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Then, we are creating a SessionLocal.
# Once we create an instance of the SessionLocal class, this instance will be the actual
# database session. Remember this thing, we will create an actual database session for
# each request later.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
