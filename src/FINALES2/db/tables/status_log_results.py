from sqlalchemy import TIMESTAMP, Column, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType

from FINALES2.db.base_class import Base


class StatusLogResult(Base):
    """
    This change will log contains a log of every status change for a result
    Class defining the quantity table with the following columns:
        uuid (UUIDType(32)): uuid of entry
        result_uuid (UUIDType(32)): uuid of the result for the status change
        status (VARCHAR): The status of the result at the load_time timestamp
        status_change_message (VARCHAR): Message for the reasoning of the status change
        load_time (Datetime):  Timestamp for when the row is added
    """

    uuid = Column(
        UUIDType(binary=False),
        primary_key=True,
        nullable=False,
    )
    result_uuid = Column(
        UUIDType(binary=False),
        ForeignKey("result.uuid"),
        nullable=False,
    )
    status = Column(
        String,
        nullable=False,
    )
    status_change_message = Column(
        String,
        nullable=True,
    )
    load_time = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
