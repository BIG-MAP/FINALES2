# from sqlalchemy import TIMESTAMP, Boolean, Column, String
# from sqlalchemy import ForeignKey
# from sqlalchemy.sql import func
# from sqlalchemy_utils import UUIDType
# from sqlalchemy.orm import relationship

# from FINALES2.db.base_class import Base


# class LinkQuantityResult(Base):
#     """
#     Class defining the quantity table with the following columns:
#         link_uuid (UUIDType (32)):
#         quantity_uuid (UUIDType (32)):
#         result_uuid (UUIDType (32)):
#         load_time (Datetime):  Timestamp for when the row is added
#     """
#     Base.__tablename__ = "link_quantity_result"

#     link_uuid = Column(
#         UUIDType(binary=False),
#         primary_key=True,
#         nullable=False,
#     )
#     quantity_uuid = Column(
#         UUIDType(binary=False),
#         ForeignKey("quantity.uuid"),
#         nullable=False,
#     )
#     resuelt_uuid = Column(
#         UUIDType(binary=False),
#         ForeignKey("result.uuid"),
#         nullable=False,
#     )
#     load_time = Column(
#         TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
#     )

#     quantity = relationship("quantity", backref="link_quantity_result")
#     result = relationship("result", backref="link_quantity_result")
