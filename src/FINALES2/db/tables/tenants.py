# import uuid

from db.base_class import Base
from sqlalchemy import Column, DateTime, String

# from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType


class Tenant(Base):
    """
    Class defining the tenant table with the following columns:
    """

    uuid = Column(
        UUIDType(binary=False),
        primary_key=True,
        # default=uuid.uuid4
    )
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
