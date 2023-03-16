from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy_utils import UUIDType

from FINALES2.db.base_class import Base


class Result(Base):
    """
    Class defining the result table with the following columns:
        uuid CHAR:                  uuid of the posted result
        request_uuid CHAR:          uuid of the original request requesting the data
        quantity VARCHAR:           Quantity of the results
        parameters VARCHAR:         JSON string of the parameters used for the result.
        data VARCHAR:               JSON string of the posted data
        posting_tenant_uuid CHAR:   uuid of the tenant posting the result
        posting_recieved_timestamp: Timestamp of the when the posting was recieved
        cost VARCHAR:
        status VARCHAR:             List with status and timestamps of the entry,
                                    with the last list entry being the current status
    load_time(DateTime):            Timestamp for when the row is added
        TODO size of the json string
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
    quantity = Column(String(Base.QUANTITY_STRING_SIZE), nullable=False)
    parameters = Column(
        String(Base.PARAMETERS_STRING_SIZE),
        nullable=False,
    )
    data = Column(String(Base.DATA_STRING_SIZE), nullable=False)
    posting_tenant_uuid = Column(
        UUIDType(binary=False),
        nullable=False,
    )
    # posting_recieved_timestamp = Column(
    #     Datetime,
    #     nullable=False,
    # )
    cost = Column(String(Base.COST_STRING_SIZE), nullable=True)
    status = Column(String(Base.STATUS_STRING_SIZE), nullable=False)
    load_time = Column(
        DateTime,
        nullable=False,
    )
