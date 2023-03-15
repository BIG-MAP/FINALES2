from datetime import datetime

from pydantic import BaseModel


class Request(BaseModel):
    quantity: str
    parameters: dict
    tenant_uuid: str


class RequestInfo(BaseModel):
    uuid: str
    ctime: datetime
    status: str
    request: Request


class Result(BaseModel):
    data: dict
    quantity: str
    parameters: dict
    tenant_uuid: str


class ResultInfo(BaseModel):
    uuid: str
    ctime: datetime
    status: str
    result: Result


class QuantityInfo(BaseModel):
    name: str
    json_schema: dict
