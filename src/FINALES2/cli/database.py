import json
import uuid
from datetime import datetime

import click

from FINALES2.db import Base, Quantity
from FINALES2.db.session import engine, get_db


@click.group("db")
def cli_db():
    """Commands to manipulate the database."""


@cli_db.command("init")
def db_init():
    "Initialize the database, with the tables for FINALES"

    click.echo("here")
    Base.metadata.create_all(bind=engine)
    click.echo("Initialized the database with the following tables:")

    for table in Base.metadata.sorted_tables:
        click.echo(f"   {table.name}")


@cli_db.command("populate")
def db_populate():
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
            #        "method": "DummyMethod",
            "specifications": json.dumps(dummy_schema),
            "is_active": True,
            "load_time": datetime.now(),
        }
    )

    with get_db() as session:
        session.add(new_capability)
        session.commit()
        session.refresh(new_capability)
