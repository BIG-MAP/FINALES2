from datetime import datetime
from uuid import UUID

from FINALES2 import schemas
from FINALES2.tenants.referenceTenant import Tenant
from FINALES2.user_management import User


def test_Tenant_toJSON():
    # instantiate tenant object for test
    meta = schemas.GeneralMetaData(
        name="testTenant", description="This is a great tenant."
    )

    operator = User(
        username="operator1",
        password="password1",
        uuid=UUID("{12345678-1234-5678-1234-567812345679}"),
        usergroups=["Project_A"],
        sleep_time_s=1,
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

    FINALES_server_config = schemas.ServerConfig(
        app_title="FINALES2",
        app_description="FINALES2 accepting requests, "
        "managing queues and serving queries",
        app_version="0.0.1",
        host="0.0.0.0",
        port=5678,
    )

    end_run_time = datetime(2023, 3, 31)

    tenant_user = User(
        username="ReferenceTenant",
        password="secretPW_forRefUsr",
        uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
        usergroups=["Project_A"],
        sleep_time_s=1,
    )

    test_tenant = Tenant(
        general_meta=meta,
        operator=operator,
        queue=[],
        quantities=quantities,
        FINALES_server_config=FINALES_server_config,
        end_run_time=end_run_time,
        tenant_user=tenant_user,
    )

    JSON_target = (
        '{"general_meta": {"name": "testTenant", "description": '
        '"This is a great tenant."}, "quantities": {"DummyQuantity": '
        '{"name": "DummyQuantity", "methods": {"DummyMethod": {"name": '
        '"myMethod", "quantity": "DummyQuantity", "parameters": '
        '["temperature"], "limitations": {"temperature": {"minimum": 5, '
        '"maximum": 20}}}}, "specifications": {"composition": {"a": 5, "b": 0.7}, '
        '"temperature": 273.15}, "is_active": true}}, "queue": [], '
        '"sleep_time_s": 1, '
        '"tenant_config": null, "FINALES_server_config": {"app_title": "FINALES2", '
        '"app_description": "FINALES2 accepting requests, managing queues '
        'and serving queries", "app_version": "0.0.1", "host": "0.0.0.0", '
        '"port": 5678}, "end_run_time": "2023-03-31T00:00:00", "operator": '
        '{"username": '
        '"operator1", "uuid": "12345678-1234-5678-1234-567812345679", "password": '
        '"password1", "usergroups": ["Project_A"]}, "tenant_user": {"username": '
        '"ReferenceTenant", "uuid": "12345678-1234-5678-1234-567812345678", '
        '"password": "secretPW_forRefUsr", "usergroups": ["Project_A"]}}'
    )

    # get the resulting JSON string
    JSON_result = test_tenant.to_json()

    # compare the two results
    assert JSON_result == JSON_target, "The JSON strings do not match."


def test_Tenant_fromJSON():
    # instantiate tenant object for test
    meta2 = schemas.GeneralMetaData(
        name="testTenant", description="This is a great tenant."
    )

    operator2 = User(
        username="operator1",
        password="password1",
        uuid=UUID("{12345678-1234-5678-1234-567812345679}"),
        usergroups=["Project_A"],
        sleep_time_s=1,
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

    FINALES_server_config2 = schemas.ServerConfig(
        app_title="FINALES2",
        app_description="FINALES2 accepting requests, "
        "managing queues and serving queries",
        app_version="0.0.1",
        host="0.0.0.0",
        port=5678,
    )

    end_run_time2 = datetime(2023, 3, 31)

    tenant_user2 = User(
        username="ReferenceTenant",
        password="secretPW_forRefUsr",
        uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
        usergroups=["Project_A"],
        sleep_time_s=1,
    )

    test_tenant2 = Tenant(
        general_meta=meta2,
        operator=operator2,
        queue=[],
        quantities=quantities2,
        FINALES_server_config=FINALES_server_config2,
        end_run_time=end_run_time2,
        sleep_time_s=1,
        tenant_user=tenant_user2,
    )

    tenant_JSON = (
        '{"general_meta": {"name": "testTenant", "description": '
        '"This is a great tenant."}, "quantities": {"DummyQuantity": '
        '{"name": "DummyQuantity", "methods": {"DummyMethod": {"name": '
        '"myMethod", "quantity": "DummyQuantity", "parameters": '
        '["temperature"], "limitations": {"temperature": {"minimum": 5, '
        '"maximum": 20}}}}, "specifications": {"composition": {"a": 5, "b": 0.7}, '
        '"temperature": 273.15}, "is_active": true}}, "queue": "[]", '
        '"tenant_config": null, "FINALES_server_config": {"app_title": "FINALES2", '
        '"app_description": "FINALES2 accepting requests, managing queues '
        'and serving queries", "app_version": "0.0.1", "host": "0.0.0.0", '
        '"port": 5678}, "end_run_time": "2023-03-31T00:00:00", "operator": '
        '{"username": '
        '"operator1", "uuid": "12345678-1234-5678-1234-567812345679", "password": '
        '"password1", "usergroups": ["Project_A"]}, "tenant_user": {"username": '
        '"ReferenceTenant", "uuid": "12345678-1234-5678-1234-567812345678", '
        '"password": "secretPW_forRefUsr", "usergroups": ["Project_A"]}, '
        '"sleep_time_s": 1}'
    )

    tenant_result2 = Tenant.from_json(tenant_JSON)

    assert tenant_result2 == test_tenant2


def test_Tenant__get_requests():
    # get the tenant for testing
    meta3 = schemas.GeneralMetaData(
        name="testTenant", description="This is a great tenant."
    )

    operator3 = User(
        username="operator1",
        password="password1",
        uuid=UUID("{12345678-1234-5678-1234-567812345679}"),
        usergroups=["Project_A"],
        sleep_time_s=1,
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

    FINALES_server_config3 = schemas.ServerConfig(
        app_title="FINALES2",
        app_description="FINALES2 accepting requests, "
        "managing queues and serving queries",
        app_version="0.0.1",
        host="0.0.0.0",
        port=13371,
    )

    end_run_time3 = datetime(2023, 3, 31)

    tenant_user3 = User(
        username="ReferenceTenant",
        password="secretPW_forRefUsr",
        uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
        usergroups=["Project_A"],
        sleep_time_s=1,
    )

    test_tenant3 = Tenant(
        general_meta=meta3,
        operator=operator3,
        queue=[],
        quantities=quantities3,
        FINALES_server_config=FINALES_server_config3,
        end_run_time=end_run_time3,
        tenant_user=tenant_user3,
    )

    # TODO: Test the remaining funcitonalities of the Tenant class
    test_tenant3
