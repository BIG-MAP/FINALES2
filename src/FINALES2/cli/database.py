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


@click.argument(
    "username",
    type=str,
)
@click.option(
    "--password",
    required=True,
    prompt="Choose a password",
    hide_input=True,
    confirmation_prompt=True,
    type=str,
    help="Password for the new user.",
)
@click.option(
    "--usergroup",
    type=str,
    multiple=True,
    help="Usergroup the user will belong to (may be used multiple times).",
)
@cli_add.command("user")
def db_add_user(username, password, usergroup):
    "Add an new user to the user management table."
    from FINALES2.user_management.user_manager import new_user

    message = new_user(username=username, password=password, usergroups=usergroup)
    click.echo(message)


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


@cli_db.group("alter-state")
def cli_alter_state():
    """Commands to alter is_active column of the tenants and capabilities."""


@click.option(
    "--input-method-name",
    required=True,
    prompt="Please provide the name of the method to deactivate",
    type=str,
    help="Name of the method to deactivate",
)
@click.option(
    "--input-answer",
    required=True,
    prompt=(
        "This is an irreversible command for the method entry. "
        "A new entry would be needed for tenants to register to the method "
        "Enter 1 if you wish to proceed"
    ),
    type=int,
    help="Name of the method to deactivate",
)
@cli_alter_state.command("deactivate-capability")
def db_deactivate_capability(input_method_name, input_answer):
    """Alter the is_active state of a cabability."""
    if input_answer != 1:
        return
    server_manager = ServerManager(database_context=get_db)
    server_manager.deactivate_capability(input_method_name)


@click.option(
    "--input-boolean",
    required=True,
    prompt="Please provide the new is_active state as a boolean integer",
    type=int,
    help="Boolean integer the is_active column should be changed to.",
)
@click.option(
    "--input-uuid",
    required=True,
    prompt="Please provide the uuid of the tenant",
    type=str,
    help="uuid string the tenant.",
)
@cli_alter_state.command("tenant")
def db_alter_tenant_state(input_uuid, input_boolean):
    "Alter the is_active state of a tenant"

    server_manager = ServerManager(database_context=get_db)
    server_manager.alter_tenant_state(input_uuid, input_boolean)


@cli_db.group("get")
def cli_retrieve():
    """Commands to retrieve information on tenants."""


@click.option(
    "--input-name",
    required=False,
    prompt="Provide input the name of the tenant to retrieve the uuid for",
    type=str,
    help=("Possible way to filter the name of a tenant to retrieve the uuid."),
)
@cli_retrieve.command("tenant-uuid")
def db_retrieve_tenant_specification(input_name=None):
    "Retrieve uuid of all tenants, or just the one with an above specified name"

    server_manager = ServerManager(database_context=get_db)
    server_manager.retrieve_tenant_uuid(input_name)
