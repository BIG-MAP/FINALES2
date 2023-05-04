from sqlalchemy import TIMESTAMP, Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType

from FINALES2.db.base_class import Base


class LinkQuantityRequest(Base):
    """
    The table will consits of one row per method stated per request.
    Class defining the quantity table with the following columns:
        link_uuid (UUIDType(32)): uuid of the link row entry
        method_uuid (UUIDType(32)): uuid of the method from the quantity table.
        request_uuid (UUIDType(32)): uuid of the request with desired methods
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
    request_uuid = Column(
        UUIDType(binary=False),
        ForeignKey("request.uuid"),
        nullable=False,
    )
    load_time = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
