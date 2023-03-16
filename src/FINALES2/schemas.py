""" This file collects all the schemas relevant in FINALES2.
This file is subject to extension. """

from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel


class ObjectBase:
    def allAttributes(self):
        attributes = User().dict()
        attributesList = list(attributes.keys())
        return attributesList

    def to_dict(self):
        return self.__dict__


class User(BaseModel, ObjectBase):
    username: str = ""
    uuid: Optional[UUID] = uuid4()
    password: str = ""
    usergroups: list[str] = []


class AccessToken(BaseModel, ObjectBase):
    access_token: str
    token_type: str


class GeneralMetaData(BaseModel):
    name: str
    description: Optional[str]


class Quantity(BaseModel):
    name: str
    methods: list[str]
    specifications: Optional[dict]
    is_active: bool


class ServerConfig(BaseModel):
    app_title: str
    app_description: str
    app_version: str
    host: str
    port: int


class Method(BaseModel):
    name: str
    quantity: str
    parameters: list  # e.g. ["temperature", "composition"]
    limitations: dict  # e.g. {"temperature": {"minimum": 10, "maximumg": 40}}


# TODO: add tenantConfig object
