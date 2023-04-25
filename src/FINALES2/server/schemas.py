"""
Note on the use of List for status: in principle, one would like
to define it like this...

    List[Tuple[datetime, str]]

But...

(1) json has no concept of tuples, so when one uses json dump it
    will store it as lists, and so using json load won't be
    directly compatible with the schema and would need extra
    translation (turning the internal lists into tuples)
    SEE: https://stackoverflow.com/q/15721363

(2) If using lists, there is no simple way of specifying the size
    and the specific types for each position.
    SEE: https://stackoverflow.com/a/44833864

So in the end, we need to keep it generic:

    List[List[Any]]

Although on second thought this schemas may be trying to do too many
things, perhaps we need 3 different layers:

 - (1) DB ORM
 - (2) Pydantic Classes based of the DB ORM
 - (3) Pydantic Classes exposed to the API

Layer 1 to 2 would take care of the translation from python types
to DB compatible types (for example, converting this list of tupples
into json and back). Layer 2 to 3 would then filter what we expose
through the API (we may not want or need to show all the status as
a list, but perhaps just the last one and without the datetime).
Also, layer 1 and 2 may be merged together if we find a way to add
pydantic checks to DB objects and maybe add the automatic translation
from python to json inside the init of the classes (or with setter
and getter like methods)

(EXTRA: maybe consider using Mapping instead of Dict)
(See: https://stackoverflow.com/a/37087556)
"""
import datetime
import json
from typing import Any, Dict, List

from pydantic import BaseModel

from FINALES2.db import Quantity as DbQuantity
from FINALES2.db import Request as DbRequest
from FINALES2.db import Result as DbResult


class Request(BaseModel):
    quantity: str
    methods: List[str]
    parameters: Dict[str, Dict[str, Any]]
    tenant_uuid: str

    @classmethod
    def from_db_request(cls, db_request: DbRequest, quantity, methods):
        """Initializes the object from the data of an orm object"""
        init_params = {
            "quantity": quantity,
            "methods": json.loads(methods),
            "parameters": json.loads(db_request.parameters),
            "tenant_uuid": str(db_request.requesting_tenant_uuid),
        }
        return cls(**init_params)


class RequestInfo(BaseModel):
    uuid: str
    ctime: datetime.datetime
    status: List[List[Any]]  # List[Tuple[datetime, str]] - see note above
    request: Request

    @classmethod
    def from_db_request(cls, db_request: DbRequest, quantity, methods):
        """Initializes the object from the data of an orm object"""
        request_internals = Request.from_db_request(db_request, quantity, methods)
        init_params = {
            "uuid": str(db_request.uuid),
            "ctime": db_request.requesting_recieved_timestamp,
            "status": json.loads(db_request.status),
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
        init_params = {
            "data": json.loads(db_result.data),
            "quantity": db_result.quantity,
            "method": json.loads(db_result.method),
            "parameters": json.loads(db_result.parameters),
            "tenant_uuid": str(db_result.posting_tenant_uuid),
            "request_uuid": str(db_result.posting_tenant_uuid),
        }
        return cls(**init_params)


class ResultInfo(BaseModel):
    uuid: str
    ctime: datetime.datetime
    status: List[List[Any]]  # List[Tuple[datetime, str]] - see note above
    result: Result


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
