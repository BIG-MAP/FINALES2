from db.base_class import Base
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy_utils import UUIDType


class Result(Base):
    """
    Class defining the result table with the following columns:
        uuid CHAR(32):                uuid of the posted result
        request_uuid CHAR(32):        uuid of the original request requesting the data
        quantity VARCHAR():           Quantity of the results
        parameters VARCHAR(5000):     JSON string of the parameters used for the result.
        data VARCHAR(5000):           JSON string of the posted data
        posting_tenant_uuid CHAR(32): uuid of the tenant posting the result
        posting_recieved_timestamp:   Timestamp of the TODO
        cost():  TODO....
        status VARCHAR(50):            List with status and timestamps of the entry,
                                       with the last
                                       list entry being the current status
        load_time(DateTime):           Timestamp for when the row is added
        TODO size of the json string
    """

    uuid = Column(
        UUIDType(binary=False),
        primary_key=True,
        # default=uuid.uuid4
    )
    request_uuid = Column(
        UUIDType(binary=False),
        ForeignKey("request.uuid"),
        nullable=False,
    )
    quantity = Column(String(50), nullable=False)
    parameters = Column(
        String(5000),
        nullable=False,
    )
    data = Column(String(5000), nullable=False)
    posting_tenant_uuid = Column(
        UUIDType(binary=False),
        nullable=False,
    )
    """
    TODO
    posting_recieved_timestamp
    cost
    status
    """
    load_time = Column(
        DateTime,
        nullable=False,
    )
