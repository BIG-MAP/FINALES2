# Base class for all the tables...

from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr

# Declarative system provided by the SQLAlchemy ORM in order to define classes mapped to
# relational database tables


@as_declarative()
class Base:
    id: Any
    __name__: str

    TENANT_NAME_STRING_SIZE = 100
    METHOD_STRING_SIZE = 100
    QUANTITY_STRING_SIZE = 100
    CAPABILITIES_STRING_SIZE = 5000
    LIMITATIONS_STRING_SIZE = 5000
    SPECIFICATIONS_STRING_SIZE = 5000
    PARAMETERS_STRING_SIZE = 5000
    DATA_STRING_SIZE = 5000
    COST_STRING_SIZE = 100
    STATUS_STRING_SIZE = 100

    # to generate tablename from classname
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
