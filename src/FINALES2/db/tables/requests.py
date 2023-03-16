from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy_utils import UUIDType

from FINALES2.db.base_class import Base


class Request(Base):
    """
    Class defining the request table with the following columns:
    """

    uuid = Column(
        UUIDType(binary=False),
        primary_key=True,
        nullable=False,
    )
    quantity = Column(String(Base.QUANTITY_STRING_SIZE), nullable=False)
    method = Column(String(Base.METHOD_STRING_SIZE), nullable=False)
    parameters = Column()

    requesting_tenant_uuid = Column(
        UUIDType(binary=False),
        ForeignKey("tenant.uuid"),
        nullable=False,
    )
    requesting_recieved_timestamp = Column()

    load_time = Column(
        DateTime,
        nullable=False,
    )
