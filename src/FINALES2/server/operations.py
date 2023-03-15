import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from jsonschema import validate

from FINALES2.server.schemas import (
    QuantityInfo,
    Request,
    RequestInfo,
    Result,
    ResultInfo,
)

operations_router = APIRouter(tags=["Data Operations"])

dummy_schema = {
    "type": "object",
    "properties": {
        "method": {"type": "string", "description": "a string describing the method"}
    },
    "required": ["method"],
}

tempdict_requests: Dict[str, Any] = {}
tempdict_results: Dict[str, Any] = {}
tempdict_quantities: Dict[str, Any] = {
    "DummyQuantity": QuantityInfo(name="DummyQuantity", json_schema=dummy_schema)
}


@operations_router.get("/requests/{object_id}")
def get_request(object_id: str) -> Optional[Request]:
    """Get request by id."""
    if object_id in tempdict_requests:
        return tempdict_requests[object_id]
    return None


@operations_router.get("/results/{object_id}")
def get_result(object_id: str) -> Optional[Result]:
    """Get result by id."""
    if object_id in tempdict_results:
        return tempdict_results[object_id]
    return None


@operations_router.post("/post/request/")
def post_request(request_data: Request) -> str:
    request_params = request_data.parameters
    output = validate(instance=request_params, schema=dummy_schema)
    print(f"all good? {output}")
    request_info = RequestInfo(
        **{
            "uuid": str(uuid.uuid4()),
            "ctime": datetime.now(),
            "status": "pending",
            "request": request_data,
        }
    )
    tempdict_requests[request_info.uuid] = request_info
    return request_info.uuid


@operations_router.post("/post/result/")
def post_result(result_data: Result) -> str:
    result_info = ResultInfo(
        **{
            "uuid": str(uuid.uuid4()),
            "ctime": datetime.now(),
            "status": "aproved",
            "result": result_data,
        }
    )
    tempdict_results[result_info.uuid] = result_info
    return result_info.uuid


@operations_router.get("/get/pending_requests/")
def get_requests() -> List[RequestInfo]:
    json_datalist = [result.dict() for result in tempdict_results.values()]
    json_datastr = json.dumps(json_datalist, indent=2, default=str)
    print(f"For reference, these are the results:\n{json_datastr}")
    return [value for value in tempdict_requests.values()]


@operations_router.get("/get/quantity_types/")
def get_quantity_types() -> List[QuantityInfo]:
    return [value for value in tempdict_quantities.values()]
