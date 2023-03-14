""" This file collects all the schemas relevant in FINALES2.
This file is subject to extension. """

import inspect
from uuid import UUID, uuid4

import strawberry


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
        id: UUID = uuid4(),
        usergroups: list[str] = [],
        **kwargs
    ):
        self.username: str = username
        self.id: UUID = id
        self.password: str = password
        self.usergroups: list[str] = usergroups


@strawberry.type
class AccessToken(ObjectBase):
    access_token: str
    token_type: str
