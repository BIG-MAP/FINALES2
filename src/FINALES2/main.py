from db.base import Base
from db.session import engine


def create_table():
    print("create_tables")
    # print(Base)
    Base.metadata.create_all(bind=engine)


def start_application():
    create_table()


start_application()
