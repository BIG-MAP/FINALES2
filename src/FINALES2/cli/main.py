import click

from FINALES2.cli.database import cli_db
from FINALES2.cli.server import cli_server


@click.group()
def finales_cli():
    """Main finales cli."""


finales_cli.add_command(cli_server)
finales_cli.add_command(cli_db)
