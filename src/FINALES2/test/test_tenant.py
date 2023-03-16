from datetime import datetime
from uuid import UUID

from FINALES2 import schemas
from FINALES2.tenants.referenceTenant import Tenant


def test_toJSON():
    # instantiate tenant object for test
    meta = schemas.GeneralMetaData(
        name="testTenant", description="This is a great tenant."
    )

    operator = schemas.User(
        username="operator1",
        password="password1",
        uuid=UUID("{12345678-1234-5678-1234-567812345679}"),
        usergroups=["Project_A"],
    )

    quant = schemas.Quantity(
        name="density",
        methods=["rollingBall"],
        specifications={"composition": {"a": 5, "b": 0.7}, "temperature": 273.15},
        is_active=True,
    )

    quantities = [quant]

    FINALESServerConfig = schemas.ServerConfig(
        app_title="FINALES2",
        app_description="FINALES2 accepting requests, "
        "managing queues and serving queries",
        app_version="0.0.1",
        host="0.0.0.0",
        port=5678,
    )

    endRuntime = datetime(2023, 3, 31)

    tenantUser = schemas.User(
        username="ReferenceTenant",
        password="secretPW_forRefUsr",
        uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
        usergroups=["Project_A"],
    )

    test_tenant = Tenant(
        generalMeta=meta,
        operator=operator,
        quantities=quantities,
        FINALESServerConfig=FINALESServerConfig,
        endRuntime=endRuntime,
        tenantUser=tenantUser,
    )

    JSON_target = (
        '{"generalMeta": {'
        '"name": "testTenant", "description": "This is a great tenant."}'
        ', "operator": {"username": "operator1", '
        '"uuid": "12345678-1234-5678-1234-567812345679", '
        '"password": "password1", "usergroups": ["Project_A"]}, '
        '"quantities": [{"name": "density", "methods": ["rollingBall"], '
        '"specifications": {"composition": {"a": 5, "b": 0.7}, '
        '"temperature": 273.15}, "is_active": true}], '
        '"tenantConfig": null, '
        '"FINALESServerConfig": {'
        '"app_title": "FINALES2", "app_description": "FINALES2 accepting requests, '
        'managing queues and serving queries", '
        '"app_version": "0.0.1", "host": "0.0.0.0", "port": 5678}, '
        '"endRuntime": "2023-03-31T00:00:00", '
        '"tenantUser": {"username": "ReferenceTenant", '
        '"uuid": "12345678-1234-5678-1234-567812345678", '
        '"password": "secretPW_forRefUsr", "usergroups": ["Project_A"]}}'
    )

    # get the resulting JSON string
    JSON_result = test_tenant.to_json()

    # compare the two results
    assert JSON_result == JSON_target, "The JSON strings do not match."


def test_fromJSON():
    # instantiate tenant object for test
    meta = schemas.GeneralMetaData(
        name="testTenant", description="This is a great tenant."
    )

    operator = schemas.User(
        username="operator1",
        password="password1",
        uuid=UUID("{12345678-1234-5678-1234-567812345679}"),
        usergroups=["Project_A"],
    )

    quant = schemas.Quantity(
        name="density",
        methods=["rollingBall"],
        specifications={"composition": {"a": 5, "b": 0.7}, "temperature": 273.15},
        is_active=True,
    )

    quantities = [quant]

    FINALESServerConfig = schemas.ServerConfig(
        app_title="FINALES2",
        app_description="FINALES2 accepting requests, "
        "managing queues and serving queries",
        app_version="0.0.1",
        host="0.0.0.0",
        port=5678,
    )

    endRuntime = datetime(2023, 3, 31)

    tenantUser = schemas.User(
        username="ReferenceTenant",
        password="secretPW_forRefUsr",
        uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
        usergroups=["Project_A"],
    )

    test_tenant = Tenant(
        generalMeta=meta,
        operator=operator,
        quantities=quantities,
        FINALESServerConfig=FINALESServerConfig,
        endRuntime=endRuntime,
        tenantUser=tenantUser,
    )

    tenant_JSON = (
        '{"generalMeta": {'
        '"name": "testTenant", "description": "This is a great tenant."}'
        ', "operator": {"username": "operator1", '
        '"uuid": "12345678-1234-5678-1234-567812345679", '
        '"password": "password1", "usergroups": ["Project_A"]}, '
        '"quantities": [{"name": "density", "methods": ["rollingBall"], '
        '"specifications": {"composition": {"a": 5, "b": 0.7}, '
        '"temperature": 273.15}, "is_active": true}], '
        '"tenantConfig": null, '
        '"FINALESServerConfig": {'
        '"app_title": "FINALES2", "app_description": "FINALES2 accepting requests, '
        'managing queues and serving queries", '
        '"app_version": "0.0.1", "host": "0.0.0.0", "port": 5678}, '
        '"endRuntime": "2023-03-31T00:00:00", '
        '"tenantUser": {"username": "ReferenceTenant", '
        '"uuid": "12345678-1234-5678-1234-567812345678", '
        '"password": "secretPW_forRefUsr", "usergroups": ["Project_A"]}}'
    )

    tenant_result = Tenant.from_json(tenant_JSON)

    assert tenant_result == test_tenant
