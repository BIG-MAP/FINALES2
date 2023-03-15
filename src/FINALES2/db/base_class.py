# Base class for all the tables...

from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr

# Declarative system provided by the SQLAlchemy ORM in order to define classes mapped to
# relational database tables


@as_declarative()
class Base:
    id: Any
    __name__: str

    # to generate tablename from classname
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
