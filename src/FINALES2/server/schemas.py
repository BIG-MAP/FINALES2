from datetime import datetime

from pydantic import BaseModel


class Request(BaseModel):
    quantity: str
    methods: str
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
    method: str
    parameters: dict
    tenant_uuid: str
    request_uuid: str


class ResultInfo(BaseModel):
    uuid: str
    ctime: datetime
    status: str
    result: Result


class CapabilityInfo(BaseModel):
    quantity: str
    method: str
    json_schema: dict
