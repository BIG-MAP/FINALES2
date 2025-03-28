from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType

from FINALES2.db.base_class import Base


class IsActiveLogTenant(Base):
    """
    Class defining the logging of the is_active of specific quantities in the quantity
    table with the following columns:
        uuid (UUIDType (32)): uuid of the entry
        quantity_uuid (UUIDType (32)): uuid of the quantity with the associated
                                       is_active type
        is_active Boolean (Boolean): status if the tenant is currently active
        is_active_change_message (String): Message associated with change. Can be left
                                           blank
        load_time (Datetime):  Timestamp for when the row is added
    """

    uuid = Column(
        UUIDType(binary=False),
        primary_key=True,
        nullable=False,
    )
    tenant_uuid = Column(
        UUIDType(binary=False),
        ForeignKey("tenant.uuid"),
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
