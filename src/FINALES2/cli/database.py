import json
import uuid

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


@cli_db.group("add")
def cli_add():
    """Commands to add data to the database."""


@click.option(
    "--input-filepath",
    required=True,
    prompt="Please provide the path to a json file with the specs",
    type=str,
    help="Path to a json file with the specs.",
)
@cli_add.command("capability")
def db_add_capability(input_filepath):
    "Add an entry to the quantity table."

    with open(input_filepath) as fileobj:
        capability_data = json.load(fileobj)

    # This should maybe be done through the engine or another internal submodule
    capability_data["uuid"] = str(uuid.uuid4())
    capability_data["quantity"] = capability_data["quantity"]
    capability_data["method"] = capability_data["method"]
    capability_data["specifications"] = json.dumps(capability_data["specifications"])
    capability_data["is_active"] = 1
    new_capability = Quantity(**capability_data)

    with get_db() as session:
        session.add(new_capability)
        session.commit()
        session.refresh(new_capability)
