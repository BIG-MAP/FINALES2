"""This module named operations.py defines an API router for various data
operations using FastAPI.

It provides API endpoints to perform CRUD operations on requests and results,
as well as retrieving the capabilities of the system. The operations include
getting a request or result by its object_id, posting new requests and results,
fetching all pending requests, and obtaining the capabilities of the system.

The module uses FastAPI's APIRouter to define the routes and handle the requests.
"""

from typing import List, Optional

from fastapi import APIRouter

from FINALES2.engine.main import Engine
from FINALES2.server.schemas import CapabilityInfo, Request, RequestInfo, Result

operations_router = APIRouter(tags=["Data Operations"])


@operations_router.get("/requests/{object_id}")
def get_request(object_id: str) -> Optional[Request]:
    """API endpoint to get requests by id."""
    engine = Engine()
    return engine.get_request(object_id)


@operations_router.get("/results/{object_id}")
def get_result(object_id: str) -> Optional[Result]:
    """API endpoint to get results by id."""
    engine = Engine()
    return engine.get_result(object_id)


@operations_router.post("/post/request/")
def post_request(request_data: Request) -> str:
    """API endpoint to post a new request."""
    engine = Engine()
    return engine.create_request(request_data)


@operations_router.post("/post/result/")
def post_result(result_data: Result) -> str:
    """API endpoint to post a new result."""
    engine = Engine()
    return engine.create_result(result_data)


@operations_router.get("/get/pending_requests/")
def get_pending_requests() -> List[RequestInfo]:
    """API endpoint to get all pending requests."""
    engine = Engine()
    return engine.get_pending_requests()


@operations_router.get("/get/result_by_request/")
def get_result_by_request(request_id: str) -> Optional[Result]:
    """API endpoint to get a result by corresponding request ID."""
    engine = Engine()
    return engine.get_result_by_request(request_id)


@operations_router.get("/get/capabilities/")
def get_capabilities(currently_available=True) -> List[CapabilityInfo]:
    """API endpoint to get all capabilities."""
    engine = Engine()
    return engine.get_capabilities(currently_available=currently_available)
