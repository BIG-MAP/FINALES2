import click
import uvicorn
from fastapi import FastAPI

from FINALES2.server.operations import operations_router
from FINALES2.userManagement import userManager


@click.group("server")
def cli_server():
    """Commands to manipulate the server."""


@cli_server.command("start")
@click.option(
    "--ip",
    required=True,
    default="localhost",
    show_default=True,
    # prompt='IP for the server (prompt)',
    type=str,
    help="IP for the server (help).",
)
@click.option(
    "--port",
    required=True,
    default=13371,
    show_default=True,
    # prompt='Please indicate the port',
    type=int,
    help="Port to be used.",
)
def server_start(ip, port):
    """Start the finales server with given ip and host."""
    app = FastAPI(
        title="FINALES2",
        description="FINALES2 accepting requests, managing queues and serving queries",
        version="0.0.1",
    )
    app.include_router(router=userManager.userRouter)
    app.include_router(router=operations_router)
    uvicorn.run(app=app, host=ip, port=port)
