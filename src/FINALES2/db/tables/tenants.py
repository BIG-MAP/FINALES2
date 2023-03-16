from sqlalchemy import TIMESTAMP, Column, String
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
        load_time (Datetime):   Timestamp for when the row is added

    """

    CONTACT_PERSON_STRING_SIZE = 100

    uuid = Column(UUIDType(binary=False), primary_key=True, nullable=False)
    name = Column(
        String(Base.TENANT_NAME_STRING_SIZE),
        nullable=False,
    )
    capabilities = Column(
        String(Base.CAPABILITIES_STRING_SIZE),
        nullable=False,
    )
    limitations = Column(
        String(Base.LIMITATIONS_STRING_SIZE),
        nullable=False,
    )
    contact_person = Column(
        String(CONTACT_PERSON_STRING_SIZE),
        nullable=False,
    )
    load_time = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
