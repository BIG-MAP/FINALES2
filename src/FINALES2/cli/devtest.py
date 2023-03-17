import json
import uuid
from datetime import datetime, timedelta

import click

from FINALES2.db import Quantity, Request
from FINALES2.db.session import get_db


@click.group("devtest")
def cli_devtest():
    """Commands useful for development and testing."""


@cli_devtest.command("populate-db")
def devtest_populate_db():
    "Populates the database with initial data for testing"

    dummy_capability_populate()
    dummy_request_populate()
    # dummy_result_populate()
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
            "status": str([3, datetime.now()]),
            "load_time": datetime.now(),
        }
    )

    session_commit(new_request)
