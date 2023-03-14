# import uuid

from db.base_class import Base
from sqlalchemy import Column, DateTime, ForeignKey, String

# from sqlalchemy.orm import relationship
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

    """

    # TODO streamline uuid with measurement
    uuid = Column(
        UUIDType(binary=False),
        primary_key=True,
        # default=uuid.uuid4
    )
    request_uuid = Column(
        UUIDType(binary=False),
        ForeignKey("request.uuid"),
        # default=uuid.uuid4() # should be function call right uuid4()?
    )
    quantity = Column(String(50), nullable=False)
    parameters = Column(
        String(5000),
        nullable=False,
    )
    data = Column(
        String(5000), nullable=False  # What could the size of the json string be? TODO
    )
    posting_tenant_uuid = Column(
        UUIDType(binary=False),
        nullable=False,
        # default=uuid.uuid4 # should be function call right uuid4()?
    )
    posting_recieved_timestamp = Column(
        DateTime,
        nullable=False,
        # Type... TODO Handle... Not sure if it should be transformed or not....
    )
    cost = Column(
        String(5000),
        nullable=True,  # TODO what type are we working with???
    )
    status = Column(String(50), nullable=False)  # list of the various status for the
    load_time = Column(
        DateTime,
        nullable=False,
    )
