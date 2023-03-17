from datetime import datetime
from uuid import UUID

from FINALES2 import schemas
from FINALES2.tenants.referenceTenant import Tenant


def test_Tenant_toJSON():
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

    method = schemas.Method(
        name="myMethod",
        quantity="DummyQuantity",
        parameters=["temperature"],
        limitations={"temperature": {"minimum": 5, "maximum": 20}},
    )

    quant = schemas.Quantity(
        name="DummyQuantity",
        methods={"DummyMethod": method},
        specifications={"composition": {"a": 5, "b": 0.7}, "temperature": 273.15},
        is_active=True,
    )

    quantities = {quant.name: quant}

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
        queue=[],
        quantities=quantities,
        FINALESServerConfig=FINALESServerConfig,
        endRuntime=endRuntime,
        tenantUser=tenantUser,
    )

    JSON_target = (
        '{"generalMeta": {"name": "testTenant", "description": '
        '"This is a great tenant."}, "quantities": {"DummyQuantity": '
        '{"name": "DummyQuantity", "methods": {"DummyMethod": {"name": '
        '"myMethod", "quantity": "DummyQuantity", "parameters": '
        '["temperature"], "limitations": {"temperature": {"minimum": 5, '
        '"maximum": 20}}}}, "specifications": {"composition": {"a": 5, "b": 0.7}, '
        '"temperature": 273.15}, "is_active": true}}, "queue": "[]", '
        '"tenantConfig": null, "FINALESServerConfig": {"app_title": "FINALES2", '
        '"app_description": "FINALES2 accepting requests, managing queues '
        'and serving queries", "app_version": "0.0.1", "host": "0.0.0.0", '
        '"port": 5678}, "endRuntime": "2023-03-31T00:00:00", "operator": {"username": '
        '"operator1", "uuid": "12345678-1234-5678-1234-567812345679", "password": '
        '"password1", "usergroups": ["Project_A"]}, "tenantUser": {"username": '
        '"ReferenceTenant", "uuid": "12345678-1234-5678-1234-567812345678", '
        '"password": "secretPW_forRefUsr", "usergroups": ["Project_A"]}}'
    )

    # get the resulting JSON string
    JSON_result = test_tenant.to_json()
    print(JSON_result)

    # compare the two results
    assert JSON_result == JSON_target, "The JSON strings do not match."


def test_Tenant_fromJSON():
    # instantiate tenant object for test
    meta2 = schemas.GeneralMetaData(
        name="testTenant", description="This is a great tenant."
    )

    operator2 = schemas.User(
        username="operator1",
        password="password1",
        uuid=UUID("{12345678-1234-5678-1234-567812345679}"),
        usergroups=["Project_A"],
    )

    method2 = schemas.Method(
        name="myMethod",
        quantity="DummyQuantity",
        parameters=["temperature"],
        limitations={"temperature": {"minimum": 5, "maximum": 20}},
    )

    quant2 = schemas.Quantity(
        name="DummyQuantity",
        methods={"DummyMethod": method2},
        specifications={"composition": {"a": 5, "b": 0.7}, "temperature": 273.15},
        is_active=True,
    )

    quantities2 = {quant2.name: quant2}

    FINALESServerConfig2 = schemas.ServerConfig(
        app_title="FINALES2",
        app_description="FINALES2 accepting requests, "
        "managing queues and serving queries",
        app_version="0.0.1",
        host="0.0.0.0",
        port=5678,
    )

    endRuntime2 = datetime(2023, 3, 31)

    tenantUser2 = schemas.User(
        username="ReferenceTenant",
        password="secretPW_forRefUsr",
        uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
        usergroups=["Project_A"],
    )

    test_tenant2 = Tenant(
        generalMeta=meta2,
        operator=operator2,
        queue=[],
        quantities=quantities2,
        FINALESServerConfig=FINALESServerConfig2,
        endRuntime=endRuntime2,
        tenantUser=tenantUser2,
    )

    tenant_JSON = (
        '{"generalMeta": {"name": "testTenant", "description": '
        '"This is a great tenant."}, "quantities": {"DummyQuantity": '
        '{"name": "DummyQuantity", "methods": {"DummyMethod": {"name": '
        '"myMethod", "quantity": "DummyQuantity", "parameters": '
        '["temperature"], "limitations": {"temperature": {"minimum": 5, '
        '"maximum": 20}}}}, "specifications": {"composition": {"a": 5, "b": 0.7}, '
        '"temperature": 273.15}, "is_active": true}}, "queue": "[]", '
        '"tenantConfig": null, "FINALESServerConfig": {"app_title": "FINALES2", '
        '"app_description": "FINALES2 accepting requests, managing queues '
        'and serving queries", "app_version": "0.0.1", "host": "0.0.0.0", '
        '"port": 5678}, "endRuntime": "2023-03-31T00:00:00", "operator": {"username": '
        '"operator1", "uuid": "12345678-1234-5678-1234-567812345679", "password": '
        '"password1", "usergroups": ["Project_A"]}, "tenantUser": {"username": '
        '"ReferenceTenant", "uuid": "12345678-1234-5678-1234-567812345678", '
        '"password": "secretPW_forRefUsr", "usergroups": ["Project_A"]}}'
    )

    tenant_result2 = Tenant.from_json(tenant_JSON)

    assert tenant_result2 == test_tenant2


def test_Tenant__get_requests():
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

    quantities3 = {quant3.name: quant3}

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
        FINALESServerConfig=FINALESServerConfig3,
        endRuntime=endRuntime3,
        tenantUser=tenantUser3,
    )

    # TODO: Test the remaining funcitonalities of the Tenant class
    test_tenant3
