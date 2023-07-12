import datetime
import json
from typing import Any, Dict, List

from pydantic import BaseModel
from sqlalchemy import select

from FINALES2.db import LinkQuantityRequest as DBLinkQuantityRequest
from FINALES2.db import LinkQuantityResult as DBLinkQuantityResult
from FINALES2.db import Quantity as DbQuantity
from FINALES2.db import Request as DbRequest
from FINALES2.db import Result as DbResult
from FINALES2.db.session import get_db


class Request(BaseModel):
    quantity: str
    methods: List[str]
    parameters: Dict[str, Dict[str, Any]]
    tenant_uuid: str

    @classmethod
    def from_db_request(cls, db_request: DbRequest):
        """Initializes the object from the data of an orm object"""

        # Retrieving methods and quantity
        query_inp = (
            select(DbQuantity.quantity, DbQuantity.method)
            .join(DBLinkQuantityRequest)
            .join(DbRequest)
            .where(db_request.uuid == DBLinkQuantityRequest.request_uuid)
            .where(DbQuantity.uuid == DBLinkQuantityRequest.method_uuid)
        )

        with get_db() as session:
            query_out = session.execute(query_inp).all()

        if len(query_out) < 1:
            raise RuntimeError(
                f"Corrupted DB! No quantity was found for request {db_request.uuid}."
            )

        # Constructs methods list
        methods = []
        quantity_former_iteration = ""

        for (
            quantity_iter,
            methods_iter,
        ) in query_out:
            # Check that quantity is the same for the methods
            if quantity_former_iteration == "":
                quantity_former_iteration = quantity_iter
            elif quantity_former_iteration != quantity_iter:
                raise RuntimeError(
                    f"Corrupted DB! Several quantities ({quantity_former_iteration}, "
                    f"{quantity_iter}) exists when retrieving the list of methods for"
                    f"request. Only a single quantity with numerous possible methods"
                    f"is expected"
                )
            methods.append(methods_iter)
        quantity = quantity_iter

        init_params = {
            "quantity": quantity,
            "methods": methods,
            "parameters": json.loads(db_request.parameters),
            "tenant_uuid": str(db_request.requesting_tenant_uuid),
        }
        return cls(**init_params)


class RequestInfo(BaseModel):
    uuid: str
    ctime: datetime.datetime
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
    data: Dict[str, Any]
    quantity: str
    method: List[str]
    parameters: Dict[str, Dict[str, Any]]
    tenant_uuid: str
    request_uuid: str

    @classmethod
    def from_db_result(cls, db_result: DbResult):
        """Initializes the object from the data of an orm object"""
        # Retrieving methods and quantity from the quantity table
        query_inp = (
            select(DbQuantity.quantity, DbQuantity.method)
            .join(DBLinkQuantityResult)
            .join(DbResult)
            .where(db_result.uuid == DBLinkQuantityResult.result_uuid)
            .where(DbQuantity.uuid == DBLinkQuantityResult.method_uuid)
        )

        with get_db() as session:
            query_out = session.execute(query_inp).all()

        if len(query_out) != 1:
            raise ValueError(
                f"Db corrupted: Several output ({len(query_out)}) for retrieval of "
                f"method and quantity related to a result, only 1 output expected"
            )

        quantity, method = query_out[0]
        init_params = {
            "data": json.loads(db_result.data),
            "quantity": quantity,
            "method": [method],
            "parameters": json.loads(db_result.parameters),
            "tenant_uuid": str(db_result.posting_tenant_uuid),
            "request_uuid": str(db_result.request_uuid),
        }
        return cls(**init_params)


class ResultInfo(BaseModel):
    uuid: str
    ctime: datetime.datetime
    status: str
    result: Result

    @classmethod
    def from_db_result(cls, db_result: DbResult):
        """Initializes the object from the data of an orm object"""
        result_internals = Result.from_db_result(db_result)
        init_params = {
            "uuid": str(db_result.uuid),
            "ctime": db_result.load_time,
            "status": db_result.status,
            "result": result_internals,
        }

        return cls(**init_params)


class CapabilityInfo(BaseModel):
    quantity: str
    method: str
    json_schema_specifications: Dict[str, Any]
    json_schema_result_output: Dict[str, Any]

    @classmethod
    def from_db_quantity(cls, db_quantity: DbQuantity):
        """Initializes the object from the data of an orm object"""
        init_params = {
            "quantity": db_quantity.quantity,
            "method": db_quantity.method,
            "json_schema_specifications": json.loads(db_quantity.specifications),
            "json_schema_result_output": json.loads(db_quantity.result_output),
        }
        return cls(**init_params)


class LimitationsInfo(BaseModel):
    quantity: str
    method: str
    limitations: Dict[str, Any]
