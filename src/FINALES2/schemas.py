""" This file collects all the schemas relevant in FINALES2.
This file is subject to extension. """

from typing import Optional

from pydantic import BaseModel


class GeneralMetaData(BaseModel):
    name: str
    description: Optional[str] = None


class Method(BaseModel):
    name: str
    quantity: str
    parameters: list  # e.g. ["temperature", "composition"]
    limitations: dict  # e.g. {"temperature": {"minimum": 10, "maximum": 40}}


class Quantity(BaseModel):
    name: str
    methods: dict[str, Method]
    specifications: Optional[dict] = None
    is_active: bool


class ServerConfig(BaseModel):
    app_title: str
    app_description: str
    app_version: str
    host: str
    port: int


# TODO: add tenantConfig object
