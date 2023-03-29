from datetime import datetime
from uuid import UUID

from FINALES2 import schemas
from FINALES2.tenants.referenceMethod import prepare_my_result, run_my_method
from FINALES2.tenants.referenceTenant import Tenant

# get the tenant for testing
meta3 = schemas.GeneralMetaData(
    name="testTenant", description="This is a great tenant."
)

operator3 = schemas.User(
    username="operator1",
    password="password1",
    uuid=UUID("{12345678-1234-5678-1234-567812345679}"),
    usergroups=["Project_A"],
)

method3 = schemas.Method(
    name="myMethod",
    quantity="DummyQuantity",
    parameters=["temperature"],
    limitations={"temperature": {"minimum": 5, "maximum": 20}},
)

quant3 = schemas.Quantity(
    name="DummyQuantity",
    methods={"DummyMethod": method3},
    specifications={"composition": {"a": 5, "b": 0.7}, "temperature": 273.15},
    is_active=True,
)

quantities3 = {"DummyQuantity": quant3}

FINALESServerConfig3 = schemas.ServerConfig(
    app_title="FINALES2",
    app_description="FINALES2 accepting requests, "
    "managing queues and serving queries",
    app_version="0.0.1",
    host="0.0.0.0",
    port=13371,
)

endRuntime3 = datetime(2023, 3, 31)

tenantUser3 = schemas.User(
    username="ReferenceTenant",
    password="secretPW_forRefUsr",
    uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
    usergroups=["Project_A"],
)


test_tenant3 = Tenant(
    generalMeta=meta3,
    operator=operator3,
    queue=[],
    quantities=quantities3,
    run_method=run_my_method,
    prepare_results=prepare_my_result,
    FINALESServerConfig=FINALESServerConfig3,
    endRuntime=endRuntime3,
    tenantUser=tenantUser3,
)


a = test_tenant3.to_json()
b = Tenant.from_json(a)
print(b)
# test_tenant3.run()
