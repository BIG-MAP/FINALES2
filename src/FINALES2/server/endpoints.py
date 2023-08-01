"""This module named operations.py defines an API router for various data
operations using FastAPI.

It provides API endpoints to perform CRUD operations on requests and results,
as well as retrieving the capabilities of the system. The operations include
getting a request or result by its object_id, posting new requests and results,
fetching all pending requests, and obtaining the capabilities of the system.

The module uses FastAPI's APIRouter to define the routes and handle the requests.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException

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
    try:
        return engine.get_request(object_id)
    except ValueError as error_message:
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=str(error_message))


@operations_router.get("/results/{object_id}")
def get_result(
    object_id: str, token: User = Depends(user_manager.get_active_user)
) -> Optional[ResultInfo]:
    """API endpoint to get results by id."""
    engine = Engine()
    try:
        return engine.get_result(object_id)
    except ValueError as error_message:
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=str(error_message))


@operations_router.post("/requests/")
def post_request(
    request_data: Request, token: User = Depends(user_manager.get_active_user)
) -> str:
    """API endpoint to post a new request."""
    engine = Engine()
    try:
        return engine.create_request(request_data)
    except ValueError as error_message:
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=str(error_message))


@operations_router.post("/results/")
def post_result(
    result_data: Result, token: User = Depends(user_manager.get_active_user)
) -> str:
    """API endpoint to post a new result."""
    engine = Engine()
    try:
        return engine.create_result(result_data)
    except ValueError as error_message:
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=str(error_message))


@operations_router.post("/results/post_unsolicited_result")
def post_result_with_no_prior_request(
    result_data: Result, token: User = Depends(user_manager.get_active_user)
) -> str:
    """API endpoint to post a new result without a prior request (unsolicited). Leave
    the request_uuid string input empty."""
    engine = Engine()
    try:
        # create request object
        request_data = {
            "quantity": result_data.quantity,
            "methods": result_data.method,
            "parameters": result_data.parameters,
            "tenant_uuid": result_data.tenant_uuid,
        }
        new_request = Request(**request_data)
        request_uuid = engine.create_request(new_request, unsolicited_result_tag=True)
        result_data.request_uuid = request_uuid
        return engine.create_result(result_data, unsolicited_result_tag=True)
    except ValueError as error_message:
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=str(error_message))


@operations_router.get("/pending_requests/")
def get_pending_requests(
    quantity: Optional[str] = None,
    method: Optional[str] = None,
    token: User = Depends(user_manager.get_active_user),
) -> List[RequestInfo]:
    """API endpoint to get all pending requests."""
    engine = Engine()
    try:
        return engine.get_pending_requests(quantity=quantity, method=method)
    except ValueError as error_message:
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=str(error_message))


@operations_router.get("/results_requested/{request_id}")
def get_results_requested(
    request_id: str, token: User = Depends(user_manager.get_active_user)
) -> Optional[ResultInfo]:
    """API endpoint to get a result by corresponding request ID."""
    engine = Engine()
    try:
        return engine.get_result_by_request(request_id)
    except ValueError as error_message:
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=str(error_message))


@operations_router.get("/results_requested/")
def get_results_requested_all(
    quantity: Optional[str] = None,
    method: Optional[str] = None,
    token: User = Depends(user_manager.get_active_user),
) -> List[ResultInfo]:
    """API endpoint to get all result available to the tenant requesting."""
    engine = Engine()
    try:
        return engine.get_all_results(quantity=quantity, method=method)
    except ValueError as error_message:
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=str(error_message))


@operations_router.get("/capabilities/")
def get_capabilities(
    currently_available: bool = True,
    token: User = Depends(user_manager.get_active_user),
) -> List[CapabilityInfo]:
    """
    API endpoint to return all (currently available) capabilities
    registered in the MAP.

    :type currently_available: bool

    :param currently_available: A flag to decide if the capabilities returned are from
        all registered tenants (if False) or only currently available ones (if True).
    """
    server_manager = ServerManager(database_context=get_db)
    try:
        return server_manager.get_capabilities(currently_available=currently_available)
    except ValueError as error_message:
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=str(error_message))


@operations_router.get("/limitations/")
def get_limitations(
    currently_available: bool = True,
    token: User = Depends(user_manager.get_active_user),
) -> List[LimitationsInfo]:
    """
    API endpoint to return all (currently available) limitations.

    :type currently_available: bool

    :param currently_available: A flag to decide if the limitations returned are
        from all tenants registered in the database (if False) or from avaliable
        tenants that are currently active (if True)
    """
    server_manager = ServerManager(database_context=get_db)
    try:
        return server_manager.get_limitations(currently_available=currently_available)
    except ValueError as error_message:
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=str(error_message))


@operations_router.post(
    "/requests/{object_id}/update_status/",
)
def post_new_status_for_request(
    request_id: str,
    new_status: RequestStatus,
    status_change_message: Optional[str] = None,
    token: User = Depends(user_manager.get_active_user),
) -> str:
    """API endpoint to change the status of a request which is currently not 'resolved'
    or 'unsolicited'.
    The possible inputs are: 'pending', 'reserved', 'retracted', with 'resolved' being
    automatically assigned when a result is posted and 'unsolicited' only being assigned
    when a result it posted without a request"""
    engine = Engine()
    try:
        return engine.change_status_request(
            request_id=request_id,
            status=new_status,
            status_change_message=status_change_message,
        )
    except ValueError as error_message:
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=str(error_message))


@operations_router.post("/results/{object_id}/update_status/")
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
    try:
        return engine.change_status_result(
            result_id=result_id,
            status=new_status,
            status_change_message=status_change_message,
        )
    except ValueError as error_message:
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=str(error_message))


@operations_router.get("/capabilities/templates/")
def get_templates(
    quantity: Optional[str] = None,
    method: Optional[str] = None,
    currently_available: bool = True,
    token: User = Depends(user_manager.get_active_user),
) -> Dict[str, Dict[str, Any]]:
    """API endpoint to get templates for the input and output schemas for the
    queried quantity and/or method. It can also provide templates for all of the
    available quantities and methods."""
    server_manager = ServerManager(database_context=get_db)
    try:
        return server_manager.get_schema_template(
            quantity=quantity,
            method=method,
            currently_available=currently_available,
        )
    except ValueError as error_message:
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=str(error_message))
