from sqlalchemy import TIMESTAMP, Column, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType

from FINALES2.db.base_class import Base


class Result(Base):
    """
    Class defining the result table with the following columns:
        uuid CHAR:                  uuid of the posted result
        request_uuid CHAR:          uuid of the original request requesting the data
        quantity VARCHAR:           Quantity of the results
        method (String):            Method used in the result post
        parameters VARCHAR:         JSON string of the parameters used for the result.
        data VARCHAR:               JSON string of the posted data
        posting_tenant_uuid CHAR:   uuid of the tenant posting the result
        posting_recieved_timestamp: Timestamp of the when the posting was recieved
        cost VARCHAR:               Cost associated with the result...
        status VARCHAR:             List with status and timestamps of the entry,
                                    with the last list entry being the current status
        load_time(DateTime):        Timestamp for when the row is added
    """

    uuid = Column(
        UUIDType(binary=False),
        primary_key=True,
        nullable=False,
    )
    request_uuid = Column(
        UUIDType(binary=False),
        ForeignKey("request.uuid"),
        nullable=False,
    )
    quantity = Column(String, nullable=False)
    method = Column(String, nullable=False)
    parameters = Column(
        String,
        nullable=False,
    )
    data = Column(String, nullable=False)
    posting_tenant_uuid = Column(
        UUIDType(binary=False),
        nullable=False,
    )

    cost = Column(String, nullable=True)
    status = Column(String, nullable=False)
    posting_recieved_timestamp = Column(
        DateTime,
        nullable=False,
    )
    load_time = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
