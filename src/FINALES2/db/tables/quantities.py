from sqlalchemy import TIMESTAMP, Column, String
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
        load_time (Datetime):  Timestamp for when the row is added
    """

    uuid = Column(
        UUIDType(binary=False),
        primary_key=True,
        nullable=False,
    )
    quantity = Column(String, nullable=False)
    method = Column(
        String,
        nullable=False,
    )
    specifications = Column(
        String,
        nullable=False,
    )
    result_output = Column(
        String,
        nullable=False,
    )
    load_time = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
