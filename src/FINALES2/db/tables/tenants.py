from sqlalchemy import TIMESTAMP, Boolean, Column, String
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType

from FINALES2.db.base_class import Base


class Tenant(Base):
    """
    Class defining the tenant table with the following columns:
        uuid CHAR:              uuid of the tenant
        name VARCHAR:           name of tenant
        capabilities VARCHAR:   capabilities of the tenant, quantity, method
        limitations VARCHAR:    limitations of the tenant within each method
        contact_person VARCHAR: contact person of the tenant
        is_active Boolean:      status if the tenant is currently active
        load_time (Datetime):   Timestamp for when the row is added

    """

    uuid = Column(UUIDType(binary=False), primary_key=True, nullable=False)
    name = Column(
        String,
        nullable=False,
    )
    capabilities = Column(
        String,
        nullable=False,
    )
    limitations = Column(
        String,
        nullable=False,
    )
    contact_person = Column(
        String,
        nullable=False,
    )
    is_active = Column(Boolean(), default=True)
    load_time = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
