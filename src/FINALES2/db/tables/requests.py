from sqlalchemy import TIMESTAMP, Column, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType

from FINALES2.db.base_class import Base


class Request(Base):
    """
    Class defining the request table with the following columns:
        uuid (UUIDType (32)):   uuid of the row quantity row entry
        quantity (String):      Type of quantity
        method (String):        List of of methods within the quantity that are
                                acceptable
        parameters (String):    Parameters requested for the all possible methods
        requesting_tenant_uuid (String): Json string with the specifications of the
                                measuremnet type
        requesting_recieved_timestamp (Boolean): Timestamp for when the request was
                                                 recieved
        bugdet (String):        Budget associated with the request...
        status (String):        List with status and timestamps of the entry,
                                with the last list entry being the current status
        load_time (Datetime):   Timestamp for when the row is added
    """

    uuid = Column(
        UUIDType(binary=False),
        primary_key=True,
        nullable=False,
    )
    quantity = Column(String(Base.QUANTITY_STRING_SIZE), nullable=False)
    method = Column(String(Base.METHOD_STRING_SIZE), nullable=False)
    parameters = Column(String(Base.PARAMETERS_STRING_SIZE), nullable=False)
    requesting_tenant_uuid = Column(
        UUIDType(binary=False),
        ForeignKey("tenant.uuid"),
        nullable=False,
    )
    requesting_recieved_timestamp = Column(DateTime, nullable=False)
    budget = Column(String(Base.BUDGET_STRING_SIZE), nullable=True)
    status = Column(String(Base.STATUS_STRING_SIZE), nullable=False)
    load_time = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
