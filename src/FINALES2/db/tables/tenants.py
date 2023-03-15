from db.base_class import Base
from sqlalchemy import Column, DateTime, String
from sqlalchemy_utils import UUIDType


class Tenant(Base):
    """
    Class defining the tenant table with the following columns:
    """

    id = Column(UUIDType(binary=False), primary_key=True, nullable=False)
    name = Column(
        String(1000),
        nullable=False,
    )

    """
    TODO
    THE REMANING COLUMNS SPECIFIED
    capabilities,
    limitations,
    config...(From the board, unsure what...)
    """
    load_time = Column(
        DateTime,
        nullable=False,
    )
