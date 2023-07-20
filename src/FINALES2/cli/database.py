import json

import click

from FINALES2.db import Base
from FINALES2.db.session import engine, get_db
from FINALES2.engine.server_manager import ServerManager


@click.group("db")
def cli_db():
    """Commands to manipulate the database."""


@cli_db.command("init")
def db_init():
    "Initialize the database, with the tables for FINALES"
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

    server_manager = ServerManager(database_context=get_db)
    server_manager.add_capability(capability_data)


@click.option(
    "--input-filepath",
    required=True,
    prompt="Please provide the path to a json file with the specs",
    type=str,
    help="Path to a json file with the specs.",
)
@cli_add.command("tenant")
def db_add_tenant(input_filepath):
    "Add an entry to the tenant table."

    with open(input_filepath) as fileobj:
        setup_data = json.load(fileobj)

    server_manager = ServerManager(database_context=get_db)
    server_manager.add_tenant(setup_data)
