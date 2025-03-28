from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType

from FINALES2.db.base_class import Base


class IsActiveLogQuantity(Base):
    """
    Class defining the logging of the is_active of specific quantities in the quantity
    table with the following columns:
        uuid (UUIDType (32)): uuid of the entry
        quantity_uuid (UUIDType (32)): uuid of the quantity with the associated
                                       is_active type
        is_active (Boolean):    1 - row is active when added. Row will remain active
                                with 1, but an update on the same quantity will be a new
                                row (newer load_time).
                                When a row with is_active=0 is added, it will mean the
                                type is not active, until a new is_active=1 with newer
                                load_time is added.
        is_active_change_message
        load_time (Datetime):  Timestamp for when the row is added
    """

    uuid = Column(
        UUIDType(binary=False),
        primary_key=True,
        nullable=False,
    )
    quantity_uuid = Column(
        UUIDType(binary=False),
        ForeignKey("quantity.uuid"),
        nullable=False,
    )
    is_active = Column(Boolean(), default=True)
    is_active_change_message = Column(
        String,
        nullable=False,
    )
    load_time = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
