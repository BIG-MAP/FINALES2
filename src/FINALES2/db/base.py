# db > base.py
from db.base_class import Base
from db.tables.quantities import Quantity
from db.tables.requests import Request
from db.tables.results import Result
from db.tables.tenants import Tenant

assert Base
assert Quantity
assert Request
assert Result
assert Tenant
