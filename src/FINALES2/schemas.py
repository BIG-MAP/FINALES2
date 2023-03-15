""" This file collects all the schemas relevant in FINALES2.
This file is subject to extension. """

import inspect
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import strawberry
from pydantic import BaseModel


@strawberry.interface
class ObjectBase:
    def allAttributes(self):
        attributes = inspect.getfullargspec(self.__init__).args
        attributes.remove("self")
        return attributes

    def to_dict(self):
        return self.__dict__


@strawberry.type
class User(ObjectBase):
    def __init__(
        self,
        username: str = "",
        password: str = "",
        uuid: UUID = uuid4(),
        usergroups: list[str] = [],
        **kwargs
    ):
        self.username: str = username
        self.id: UUID = uuid
        self.password: str = password
        self.usergroups: list[str] = usergroups


@strawberry.type
class AccessToken(ObjectBase):
    access_token: str
    token_type: str


class GeneralMetaData(BaseModel):
    name: str
    description: Optional[str]
    uuid: UUID


class Quantity(BaseModel):
    name: str
    methods: list[str]
    specifications: dict
    is_active: bool
    uuid: Optional[UUID]
    load_time: Optional[datetime]


class ServerConfig(BaseModel):
    app_title: str
    app_description: str
    app_version: str
    host: str
    port: int


class Method(BaseModel):
    name: str
    quantity: str
    parameters: dict
    limitations: list
