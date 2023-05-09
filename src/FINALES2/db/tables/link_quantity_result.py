from sqlalchemy import TIMESTAMP, Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType

from FINALES2.db.base_class import Base


class LinkQuantityResult(Base):
    """
    Class defining the quantity table with the following columns:
        link_uuid (UUIDType (32)): uuid of the link row entry
        method_uuid (UUIDType (32)): uuid of the method for the posted result
        result_uuid (UUIDType (32)): uuid of the posted result
        load_time (Datetime):  Timestamp for when the row is added
    """

    link_uuid = Column(
        UUIDType(binary=False),
        primary_key=True,
        nullable=False,
    )
    method_uuid = Column(
        UUIDType(binary=False),
        ForeignKey("quantity.uuid"),
        nullable=False,
    )
    result_uuid = Column(
        UUIDType(binary=False),
        ForeignKey("result.uuid"),
        nullable=False,
    )
    load_time = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
