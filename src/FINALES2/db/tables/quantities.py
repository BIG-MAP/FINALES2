from db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy_utils import UUIDType


class Quantity(Base):
    """
    Class defining the quantity table with the following columns:
        uuid (UUIDType (32)): UUID of the row quantity row entry
        quantity (String): Type of quantity
        specification (String): Json string with the specifications of the measuremnet
                                type, TODO
        is_active (Boolean): 1 - row is active when added. Row will remain active with
                             1, but an update on the same quantity will be a new row
                             (newer load_time).
                             When a row with is_active=0 is added, it will mean the type
                             is not active, until a new is_active=1 with newer load_time
                             is added.
        load_time (Datetime): Timestamp for when the row is added


        TODO size of the json string
    """

    uuid = Column(
        UUIDType(binary=False),
        primary_key=True,
    )
    quantity = Column(String(50), nullable=False)  # TODO String(size)??
    specifications = Column(
        String(5000),
        nullable=False,
    )
    is_active = Column(Boolean(), default=True)
    load_time = Column(
        DateTime,
        nullable=False,
    )
