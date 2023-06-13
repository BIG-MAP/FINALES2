from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel


class User(BaseModel):
    username: str = ""
    uuid: Optional[UUID] = uuid4()
    password: str = ""
    usergroups: list[str] = []


class AccessToken(BaseModel):
    access_token: str
    token_type: str
