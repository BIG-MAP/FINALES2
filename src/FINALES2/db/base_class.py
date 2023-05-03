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
        """
        Construct table name from classs name, which is lower case with _ for word
        seperation
        """

        upper_case = [i for i, char in enumerate(cls.__name__) if char.isupper()]

        # The iteration is backwards
        i = -1
        name = cls.__name__.lower()
        while True:
            # Break if first letter is reached
            if i == -len(upper_case):
                break

            index = upper_case[i]
            name = name[:index] + "_" + name[index:]

            i -= 1

        return name
