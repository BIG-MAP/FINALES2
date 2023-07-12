"""This module named operations.py defines an API router for various data
operations using FastAPI.

It provides API endpoints to perform CRUD operations on requests and results,
as well as retrieving the capabilities of the system. The operations include
getting a request or result by its object_id, posting new requests and results,
fetching all pending requests, and obtaining the capabilities of the system.

The module uses FastAPI's APIRouter to define the routes and handle the requests.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends

from FINALES2.engine.main import Engine, RequestStatus, ResultStatus, get_db
from FINALES2.engine.server_manager import ServerManager
from FINALES2.server.schemas import (
    CapabilityInfo,
    LimitationsInfo,
    Request,
    RequestInfo,
    Result,
    ResultInfo,
)
from FINALES2.user_management import user_manager
from FINALES2.user_management.classes_user_manager import User

operations_router = APIRouter(tags=["Data Operations"])


@operations_router.get("/requests/{object_id}")
def get_request(
    object_id: str, token: User = Depends(user_manager.get_active_user)
) -> Optional[RequestInfo]:
    """API endpoint to get requests by id."""
    engine = Engine()
    return engine.get_request(object_id)


@operations_router.get("/results/{object_id}")
def get_result(
    object_id: str, token: User = Depends(user_manager.get_active_user)
) -> Optional[ResultInfo]:
    """API endpoint to get results by id."""
    engine = Engine()
    return engine.get_result(object_id)


@operations_router.post("/requests/")
def post_request(
    request_data: Request, token: User = Depends(user_manager.get_active_user)
) -> str:
    """API endpoint to post a new request."""
    engine = Engine()
    return engine.create_request(request_data)


@operations_router.post("/results/")
def post_result(
    result_data: Result, token: User = Depends(user_manager.get_active_user)
) -> str:
    """API endpoint to post a new result."""
    engine = Engine()
    return engine.create_result(result_data)


@operations_router.get("/pending_requests/")
def get_pending_requests(
    quantity: Optional[str] = None,
    method: Optional[str] = None,
    token: User = Depends(user_manager.get_active_user),
) -> List[RequestInfo]:
    """API endpoint to get all pending requests."""
    engine = Engine()
    return engine.get_pending_requests(quantity=quantity, method=method)


@operations_router.get("/results_requested/{request_id}")
def get_results_requested(
    request_id: str, token: User = Depends(user_manager.get_active_user)
) -> Optional[ResultInfo]:
    """API endpoint to get a result by corresponding request ID."""
    engine = Engine()
    return engine.get_result_by_request(request_id)


@operations_router.get("/results_requested/")
def get_results_requested_all(
    quantity: Optional[str] = None,
    method: Optional[str] = None,
    token: User = Depends(user_manager.get_active_user),
) -> List[ResultInfo]:
    """API endpoint to get all result available to the tenant requesting."""
    engine = Engine()
    return engine.get_all_results(quantity=quantity, method=method)


@operations_router.get("/capabilities/")
def get_capabilities(
    currently_available=True, token: User = Depends(user_manager.get_active_user)
) -> List[CapabilityInfo]:
    """API endpoint to get all capabilities."""
    server_manager = ServerManager(database_context=get_db)
    return server_manager.get_capabilities(currently_available=currently_available)


@operations_router.get("/limitations/")
def get_limitations(
    currently_available=True,
    token: User = Depends(user_manager.get_active_user),
) -> List[LimitationsInfo]:
    """API endpoint to get all limitations."""
    server_manager = ServerManager(database_context=get_db)
    return server_manager.get_limitations(currently_available=currently_available)


@operations_router.post("/requests/{object_id}/new_status_request/")
def post_new_status_for_request(
    request_id: str,
    new_status: RequestStatus,
    status_change_message: Optional[str] = None,
    token: User = Depends(user_manager.get_active_user),
) -> str:
    """API endpoint to change the status of a request which is currently not resolved.
    The possible inputs are: pending, reserved, retracted, with resolved being auto-
    matically designed when a result is posted"""
    engine = Engine()
    return engine.change_status_request(
        request_id=request_id,
        status=new_status,
        status_change_message=status_change_message,
    )


@operations_router.post("/result/{object_id}/new_status_result/")
def post_new_status_for_result(
    result_id: str,
    new_status: ResultStatus,
    status_change_message: Optional[str] = None,
    token: User = Depends(user_manager.get_active_user),
) -> str:
    """API endpoint to change the status of a result.
    The possible inputs are: deleted and amended, with original being reserved for the
    initial posting"""
    engine = Engine()
    return engine.change_status_result(
        result_id=result_id,
        status=new_status,
        status_change_message=status_change_message,
    )
