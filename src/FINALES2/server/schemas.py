import json
from datetime import datetime

from pydantic import BaseModel

from FINALES2.db import Quantity as DbQuantity
from FINALES2.db import Request as DbRequest
from FINALES2.db import Result as DbResult


class Request(BaseModel):
    quantity: str
    methods: str
    parameters: dict
    tenant_uuid: str

    @classmethod
    def from_db_request(cls, db_request: DbRequest):
        """Initializes the object from the data of an orm object"""
        init_params = {
            "quantity": db_request.quantity,
            "methods": json.loads(db_request.methods),
            "parameters": json.loads(db_request.parameters),
            "tenant_uuid": str(db_request.requesting_tenant_uuid),
        }
        return cls(**init_params)


class RequestInfo(BaseModel):
    uuid: str
    ctime: datetime
    status: str
    request: Request

    @classmethod
    def from_db_request(cls, db_request: DbRequest):
        """Initializes the object from the data of an orm object"""
        request_internals = Request.from_db_request(db_request)

        init_params = {
            "uuid": str(db_request.uuid),
            "ctime": db_request.requesting_recieved_timestamp,
            "status": db_request.status,
            "request": request_internals,
        }

        return cls(**init_params)


class Result(BaseModel):
    data: dict
    quantity: str
    method: str
    parameters: dict
    tenant_uuid: str
    request_uuid: str

    @classmethod
    def from_db_result(cls, db_result: DbResult):
        """Initializes the object from the data of an orm object"""
        init_params = {
            "data": json.loads(db_result.data),
            "quantity": db_result.quantity,
            "method": "none",
            "parameters": json.loads(db_result.parameters),
            "tenant_uuid": str(db_result.posting_tenant_uuid),
            "request_uuid": str(db_result.posting_tenant_uuid),
        }
        return cls(**init_params)


class ResultInfo(BaseModel):
    uuid: str
    ctime: datetime
    status: str
    result: Result


class CapabilityInfo(BaseModel):
    quantity: str
    method: str
    json_schema: dict

    @classmethod
    def from_db_quantity(cls, db_quantity: DbQuantity):
        """Initializes the object from the data of an orm object"""
        init_params = {
            "quantity": db_quantity.quantity,
            "method": db_quantity.method,
            "json_schema": json.loads(db_quantity.specifications),
        }
        return cls(**init_params)
