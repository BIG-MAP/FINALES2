import json
import uuid
from datetime import datetime

import click

from FINALES2.db import Quantity
from FINALES2.db.session import get_db


@click.group("devtest")
def cli_devtest():
    """Commands useful for development and testing."""


@cli_devtest.command("populate-db")
def devtest_populate_db():
    "Populates the database with initial data for testing"

    dummy_schema = {
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
            "specifications": json.dumps(dummy_schema),
            "is_active": True,
            "load_time": datetime.now(),
        }
    )

    with get_db() as session:
        session.add(new_capability)
        session.commit()
        session.refresh(new_capability)
