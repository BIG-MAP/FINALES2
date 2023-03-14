from db.base import Base
from db.session import engine


def create_table():
    Base.metadata.create_all(bind=engine)
    print("The following tables have been created")
    for table in Base.metadata.sorted_tables:
        print(f"   {table.name}")


def start_application():
    create_table()


start_application()
