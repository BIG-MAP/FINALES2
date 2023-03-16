from sqlalchemy import Column, DateTime, String
from sqlalchemy_utils import UUIDType

from FINALES2.db.base_class import Base


class Tenant(Base):
    """
    Class defining the tenant table with the following columns:
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
        DateTime,
        nullable=False,
    )
