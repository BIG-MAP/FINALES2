from db.base import Base
from db.session import engine

# Dummy main.py to create the tables


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("The following tables have been created")
    for table in Base.metadata.sorted_tables:
        print(f"   {table.name}")


create_tables()
