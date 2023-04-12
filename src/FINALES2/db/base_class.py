# Base class for all the tables...

from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr

# Declarative system provided by the SQLAlchemy ORM in order to define classes mapped to
# relational database tables


@as_declarative()
class Base:
    id: Any
    __name__: str

    # Small string requirements
    TENANT_NAME_STRING_SIZE = 100
    METHOD_STRING_SIZE = 100
    QUANTITY_STRING_SIZE = 100
    COST_STRING_SIZE = 100
    BUDGET_STRING_SIZE = COST_STRING_SIZE
    STATUS_STRING_SIZE = 100
    CONTACT_PERSON_STRING_SIZE = 100

    # Large string requirements
    CAPABILITIES_STRING_SIZE = 5000
    LIMITATIONS_STRING_SIZE = 5000
    SPECIFICATIONS_STRING_SIZE = 5000
    PARAMETERS_STRING_SIZE = 5000
    DATA_STRING_SIZE = 5000
    RESULT_STRING_SIZE = 5000

    # to generate tablename from classname
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
