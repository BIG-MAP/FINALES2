from sqlalchemy import TIMESTAMP, Boolean, Column, String
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType

from FINALES2.db.base_class import Base


class Quantity(Base):
    """
    Class defining the quantity table with the following columns:
        uuid (UUIDType (32)):   uuid of the row quantity row entry
        quantity (String):      Type of quantity
        method (String):        Type of method within the quantity
        specification (String): Json string with the specifications of the measuremnet
                                type
        is_active (Boolean):    1 - row is active when added. Row will remain active
                                with 1, but an update on the same quantity will be a new
                                row (newer load_time).
                                When a row with is_active=0 is added, it will mean the
                                type is not active, until a new is_active=1 with newer
                                load_time is added.
        load_time (Datetime):  Timestamp for when the row is added
    """

    uuid = Column(
        UUIDType(binary=False),
        primary_key=True,
        nullable=False,
    )
    quantity = Column(String(Base.QUANTITY_STRING_SIZE), nullable=False)
    method = Column(
        String(Base.METHOD_STRING_SIZE),
        nullable=False,
    )
    specifications = Column(
        String(Base.SPECIFICATIONS_STRING_SIZE),
        nullable=False,
    )
    is_active = Column(Boolean(), default=True)
    load_time = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
