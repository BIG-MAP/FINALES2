import json
import uuid
from datetime import datetime

import click

from FINALES2.db import Quantity, Tenant  # , LinkQuantityRequest
from FINALES2.db.session import get_db
from FINALES2.engine.main import Engine
from FINALES2.server.schemas import Request, Result


@click.group("devtest")
def cli_devtest():
    """Commands useful for development and testing."""


@cli_devtest.command("populate-db")
def devtest_populate_db():
    "Populates the database with initial data for testing"

    dummy_capability_populate()
    present_request_id = dummy_request_populate()
    dummy_result_populate(present_request_id)
    dummy_tenant_populate()


def session_commit(input):
    with get_db() as session:
        session.add(input)
        session.commit()
        session.refresh(input)
    return


def dummy_capability_populate():
    dummy_specification_schema = {
        "properties": {
            "temperature": {
                "type": "number",
                "description": (
                    "the temperature of the system"
                    " (this is just a temporary stand in)"
                ),
            }
        },
        "required": ["internal_temperature"],
    }

    dummy_result_output_schema = {
        "Dummy": "Dummy"
        # Setup depends on the output given by Fransisco TODO
    }

    new_capability = Quantity(
        **{
            "uuid": str(uuid.uuid4()),
            "quantity": "DummyQuantity",
            "method": "DummyMethod",
            "specifications": json.dumps(dummy_specification_schema),
            "result_output": json.dumps(dummy_result_output_schema),
            "is_active": True,
            "load_time": datetime.now(),
        }
    )

    session_commit(new_capability)


def dummy_request_populate():
    dummy_parameters_schema = {
        "DummyMethod": {
            "internal_temperature": {
                "value": 42,
                "type": "number",
                "description": (
                    "the internal temperature asked for by the request in Method1"
                    " (this is just a temporary stand in)"
                ),
            }
        },
    }

    new_request = Request(
        **{
            "quantity": "DummyQuantity",
            "methods": ["DummyMethod"],
            "parameters": dummy_parameters_schema,
            "tenant_uuid": str(uuid.uuid4()),
        }
    )

    engine = Engine()
    present_request_id = engine.create_request(new_request)

    return present_request_id


def dummy_result_populate(present_request_id):
    dummy_parameters_schema = {
        "DummyMethod": {
            "internal_temperature": {
                "value": 42,
                "type": "number",
                "description": (
                    "the internal temperature used for the posted Method1 result"
                    " (this is just a temporary stand in)"
                ),
            },
            "voltage_setting": {
                "value": 2,
                "type": "number",
                "description": (
                    "the voltage setting used for the posted Method1 result"
                    " (this is just a temporary stand in)"
                ),
            },
        },
    }

    dummy_data_schema = {
        "density(method1)": {
            "type": "number",
            "value": 33,
        },
    }

    new_result = Result(
        **{
            "request_uuid": present_request_id,
            "quantity": "DummyQuantity",
            "method": ["DummyMethod"],
            "parameters": dummy_parameters_schema,
            "data": dummy_data_schema,
            "tenant_uuid": str(uuid.uuid4()),
        }
    )

    engine = Engine()
    engine.create_result(new_result)


def dummy_tenant_populate():
    dummy_capabilities_schema = {
        "quantity1": {
            "method1": {
                "unit_of_measurement": "Dummy_unit1",
                "necessary_input_for_method": {
                    "voltage": {
                        "type": "number",
                        "unit": "mV",
                        "description": "Description of the voltage needed",
                    },
                    "temperature": {
                        "type": "number",
                        "unit": "K",
                        "description": "Description of the temp. needed",
                    },
                },
            },
            "method2": {
                "unit_of_measurement": "Dummy_unit2",
                "necessary_input_for_method": {
                    "internal_temperature": {
                        "type": "number",
                        "unit": "K",
                        "description": "Description of the internal temp. needed",
                    }
                },
            },
        },
        "quantity2": {
            "method3": {
                "unit_of_measurement": "Dummy_unit3",
                "necessary_input_for_method": {
                    "functional": {
                        "type": "str",
                        "input_str": "PBE",
                        "description": (
                            "Description of the functional needed (simulation)"
                        ),
                    },
                },
            },
        },
    }
    # type string for an input will not be accompanied by a unit...
    #  TODO for tenant reference

    dummy_limitations_schema = {
        "quantity1": {
            "method1": {
                "range_for_measurement": {"from": 0.1, "to": 10, "unit": "Dummy_unit1"},
                "range_for_parameters": {
                    "voltage": {"from": 0.1, "to": 1000, "unit": "mV"},
                    "temperature": {"from": 100, "to": 400, "unit": "K"},
                },
            },
            "method2": {
                "range_for_measurement": {
                    "from": 11,
                    "to": 12,
                    "unit": "Dummy_unit2",
                },
                "range_for_parameters": {
                    "internal_temperature": {"from": 100, "to": 200, "unit": "K"}
                },
            },
        },
        "quantity2": {
            "method3": {
                "range_for_measurement": {
                    "from": 0,
                    "to": 10000,
                    "unit": "Dummy_unit3",
                },
                "range_for_parameters": {
                    "functional": {"possible_input_str": ["PBE", "B3LYP"]}
                },
            },
        },
    }

    new_tenant = Tenant(
        **{
            "uuid": str(uuid.uuid4()),
            "name": "DTU - Dummy Technical University name",
            "capabilities": json.dumps(dummy_capabilities_schema),
            "limitations": json.dumps(dummy_limitations_schema),
            "contact_person": "Firstname Lastname, email_of_dummy@dtu.dk",
            "load_time": datetime.now(),
        }
    )

    session_commit(new_tenant)
