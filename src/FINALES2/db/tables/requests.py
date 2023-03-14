# import uuid

from db.base_class import Base
from sqlalchemy import Column, DateTime, ForeignKey, String

# from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType


class Request(Base):
    """
    Class defining the request table with the following columns:
    """

    uuid = Column(
        UUIDType(binary=False),
        primary_key=True,
        # default=uuid.uuid4
    )
    quantity = Column(String(50), nullable=False)
    tenant_uuid = Column(
        UUIDType(binary=False),
        ForeignKey("tenant.uuid"),
        # default=uuid.uuid4
    )
    """
    TODO
    THE REMANING COLUMNS SPECIFIED
    """
    load_time = Column(
        DateTime,
        nullable=False,
    )
