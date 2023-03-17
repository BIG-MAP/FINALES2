import json
import uuid
from datetime import datetime, timedelta

import click

from FINALES2.db import Quantity, Request, Result
from FINALES2.db.session import get_db


@click.group("devtest")
def cli_devtest():
    """Commands useful for development and testing."""


@cli_devtest.command("populate-db")
def devtest_populate_db():
    "Populates the database with initial data for testing"

    dummy_capability_populate()
    dummy_request_populate()
    dummy_result_populate()
    # dummy_tenant_populate()


def session_commit(input):
    with get_db() as session:
        session.add(input)
        session.commit()
        session.refresh(input)
    return


def dummy_capability_populate():
    dummy_specification_schema = {
        "type": "object",
        "properties": {
            "temperature": {
                "type": "number",
                "description": (
                    "the temperature of the system"
                    " (this is just a temporary stand in)"
                ),
            }
        },
        "required": ["temperature"],
    }

    new_capability = Quantity(
        **{
            "uuid": str(uuid.uuid4()),
            "quantity": "DummyQuantity",
            "method": "DummyMethod",
            "specifications": json.dumps(dummy_specification_schema),
            "is_active": True,
            "load_time": datetime.now(),
        }
    )

    session_commit(new_capability)


def dummy_request_populate():
    dummy_parameters_schema = {
        "type": "object",
        "DummyMethod1": {
            "interna_temperature": {
                "value": 42,
                "type": "number",
                "description": (
                    "the internal temperature asked for by the request in Method1"
                    " (this is just a temporary stand in)"
                ),
            }
        },
        "DummyMethod2": {
            "surrounding_temperature": {
                "value": 101,
                "type": "number",
                "description": (
                    "the surrounding temperature asked for by the request in Method2"
                    " (this is just a temporary stand in)"
                ),
            }
        },
    }

    new_request = Request(
        **{
            "uuid": str(uuid.uuid4()),
            "quantity": "DummyQuantity",
            "methods": str(["DummyMethod1", "DummyMethod2"]),
            "parameters": json.dumps(dummy_parameters_schema),
            "requesting_tenant_uuid": str(uuid.uuid4()),
            "requesting_recieved_timestamp": datetime.now() - timedelta(minutes=2),
            "budget": None,
            "status": str([datetime.now(), 3]),
            "load_time": datetime.now(),
        }
    )

    session_commit(new_request)


def dummy_result_populate():
    pass
    # dummy_parameters_schema = {}
    # dummy_data_schema = {}

    new_result = Result(
        **{
            "uuid": str(uuid.uuid4()),
            "request_uuid": str(uuid.uuid4()),
            "quantity": "DummyQuantity",
            "method": str(["DummyMethod1"]),
            # "parameters": json.dumps(dummy_parameters_schema),
            # "data": json.dumps(dummy_data_schema),
            "posting_tenant_uuid": str(uuid.uuid4()),
            "cost": None,
            "status": str([datetime.now(), 3]),
            # "posting_recieved_timestamp":
            "load_time": datetime.now(),
        }
    )

    assert new_result


# def dummy_tenant_populate():
#     assert Tenant
#     pass
