import click

from FINALES2.db import Base
from FINALES2.db.session import engine


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
