import json
import os
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from jsonschema import validate
from sqlalchemy import select

from FINALES2.db import LinkQuantityRequest as DbLinkQuantityRequest
from FINALES2.db import LinkQuantityResult as DbLinkQuantityResult
from FINALES2.db import Quantity as DbQuantity
from FINALES2.db import Request as DbRequest
from FINALES2.db import Result as DbResult
from FINALES2.db import StatusLogRequest as DbStatusLogRequest
from FINALES2.db import StatusLogResult as DbStatusLogResult
from FINALES2.db.session import get_db
from FINALES2.server.schemas import Request, RequestInfo, Result, ResultInfo

from . import logger


class RequestStatus(Enum):
    PENDING = "pending"
    RESERVED = "reserved"
    RESOLVED = "resolved"
    RETRACTED = "retracted"
    UNSOLICITED = "unsolicited"


class ResultStatus(Enum):
    ORIGINAL = "original"
    DELETED = "deleted"
    AMENDED = "amended"


class Engine:
    """This class is the outermost manager of the functionalities of finales."""

    def get_request(self, object_id: str) -> Optional[RequestInfo]:
        """Retrieve a request entry from the database by id."""
        query_inp = select(DbRequest).where(DbRequest.uuid == uuid.UUID(object_id))
        with get_db() as session:
            query_out = session.execute(query_inp).all()

        if len(query_out) == 0:
            return None

        api_response = RequestInfo.from_db_request(query_out[0][0])
        return api_response

    def get_result(self, object_id: str) -> Optional[ResultInfo]:
        """Retrieve a result entry from the database by id."""
        query_inp = select(DbResult).where(DbResult.uuid == uuid.UUID(object_id))
        with get_db() as session:
            query_out = session.execute(query_inp).all()

        if len(query_out) == 0:
            return None
        api_response = ResultInfo.from_db_result(query_out[0][0])
        return api_response

    def create_request(
        self, request_data: Request, unsolicited_result_tag=False
    ) -> str:
        """Create a new request entry in the database.

        This method will first validate the parameters of the request with
        the internal schema that corresponds to the quantity + method
        capability.

        Then the uuid corresponding to the method for the request will be retrieved
        to be stored with the request.

        When creating the request object, it assigns a new uuid (and returns it).
        """
        self.validate_submission(
            request_data.quantity, request_data.methods, request_data.parameters
        )
        ctime = datetime.now()

        request_uuid = str(uuid.uuid4())
        request_obj = DbRequest(
            **{
                "uuid": request_uuid,
                "parameters": json.dumps(request_data.parameters),
                "requesting_tenant_uuid": request_data.tenant_uuid,
                "requesting_recieved_timestamp": ctime,
                "budget": "not currently implemented in the API",
                "status": RequestStatus.PENDING.value,
            }
        )

        status_log_obj = DbStatusLogRequest(
            **{
                "uuid": str(uuid.uuid4()),
                "request_uuid": request_uuid,
                "status": RequestStatus.PENDING.value,
                "status_change_message": "The requests was created in the server",
            }
        )

        # Tag reserved for a request that is triggered by posting data with no prior
        # request (unsolicited)
        if unsolicited_result_tag:
            request_obj.status = RequestStatus.UNSOLICITED.value
            status_log_obj.status = RequestStatus.UNSOLICITED.value

        link_uuid = str(uuid.uuid4())
        with get_db() as session:
            # Add the request to the session
            session.add(request_obj)
            session.add(status_log_obj)

            # Loop thorugh the methods to add entries to DbLinkQuantityRequest
            list_of_link_quantity_request_obj = []
            for method_name in request_data.methods:
                # Find uuid for method in quantity table
                query_inp_method = (
                    select(DbQuantity.uuid)
                    .where(DbQuantity.quantity == request_data.quantity)
                    .where(DbQuantity.method == method_name)
                    .where(DbQuantity.is_active == 1)
                )
                query_out = session.execute(query_inp_method).all()

                # Check that the query output sizes is as intended
                if len(query_out) != 1:
                    logger.raise_value_error(
                        logger=logger,
                        msg=(
                            f"The method {method_name} for quantity "
                            f"{request_data.quantity} has several entries "
                            f"({len(query_out)}) in the quantity table which are active"
                        ),
                    )

                uuid_method = query_out[0][0]

                link_quantity_request_obj = DbLinkQuantityRequest(
                    **{
                        "link_uuid": link_uuid,
                        "method_uuid": uuid_method,
                        "request_uuid": request_uuid,
                    }
                )
                list_of_link_quantity_request_obj.append(link_quantity_request_obj)
                session.add(link_quantity_request_obj)

            session.commit()
            session.refresh(request_obj)
            session.refresh(status_log_obj)
            for link_object in list_of_link_quantity_request_obj:
                session.refresh(link_object)

        return str(request_obj.uuid)

    def create_result(self, received_data: Result, unsolicited_result_tag=False) -> str:
        """Create a new result entry in the database.

        This method will first validate the parameters of the request with
        the internal schema that corresponds to the quantity + method
        capability.

        A row is also added to the link_quantity_result table for uuid link between
        result and quantity method.

        When creating the result object, it assigns a new uuid (and returns it).
        """
        # Note: for the results we are currently using a similar structure
        # than the request, so the method is a list with a single entry and
        # the parameters is a dict with a single key, named the same as the
        # method.

        # Validations specific to posting results
        if len(received_data.method) != 1:
            logger.raise_value_error(
                logger=logger,
                msg=(
                    "Wrong length of method string for recieved result. "
                    "A list with a single method is expected, the recieved list "
                    f"{received_data.method} does not comply with this"
                ),
            )
        if len(received_data.parameters) != 1:
            logger.raise_value_error(
                logger=logger,
                msg=(
                    "Wrong number of keys in passed parameters. A single key with the "
                    "specific method was expected, the recieved parameters has the "
                    f"following keys {list(received_data.parameters.keys())} and does "
                    "not comply with this"
                ),
            )

        method_name = received_data.method[0]
        wrapped_params = {method_name: received_data.parameters[method_name]}
        self.validate_submission(
            received_data.quantity, received_data.method, wrapped_params
        )

        request_uuid = received_data.request_uuid
        query_inp = select(DbRequest).where(DbRequest.uuid == uuid.UUID(request_uuid))

        ctime = datetime.now()

        result_uuid = str(uuid.uuid4())
        db_obj = DbResult(
            **{
                "uuid": result_uuid,
                "request_uuid": request_uuid,  # get from received data and check
                "parameters": json.dumps(received_data.parameters),
                "data": json.dumps(received_data.data),
                "posting_tenant_uuid": received_data.tenant_uuid,
                "cost": "Not implemented in the API yet",
                "status": ResultStatus.ORIGINAL.value,
                "posting_recieved_timestamp": ctime,
            }
        )

        with get_db() as session:
            # Retrieve original request for the result and update request status
            query_out = session.execute(query_inp).all()
            if len(query_out) == 0:
                logger.raise_value_error(
                    logger=logger,
                    msg=f"Submitted result has no request: {request_uuid}",
                )

            session.add(db_obj)

            # Add link between method for the result and the quantity table
            query_inp_method = (
                select(DbQuantity.uuid)
                .where(DbQuantity.quantity == received_data.quantity)
                .where(DbQuantity.method == method_name)
                .where(DbQuantity.is_active == 1)
            )

            query_out_method = session.execute(query_inp_method).all()

            # Check that the query output sizes is as intended
            if len(query_out_method) != 1:
                logger.raise_value_error(
                    logger=logger,
                    msg=(
                        f"The method {method_name} for quantity "
                        f"{received_data.quantity} has several entries "
                        f"({len(query_out_method)}) in the quantity "
                        f"table which are active"
                    ),
                )

            uuid_method = query_out_method[0][0]
            link_quantity_result_obj = DbLinkQuantityResult(
                **{
                    "link_uuid": str(uuid.uuid4()),
                    "method_uuid": uuid_method,
                    "result_uuid": result_uuid,
                }
            )
            session.add(link_quantity_result_obj)

            # Log the status of the newly posted result
            result_status_log_obj = DbStatusLogResult(
                **{
                    "uuid": str(uuid.uuid4()),
                    "result_uuid": result_uuid,
                    "status": ResultStatus.ORIGINAL.value,
                    "status_change_message": "Result posted",
                }
            )

            session.add(result_status_log_obj)

            # Retrieve original request
            original_request = query_out[0][0]
            # Retrieves the object to be for changing the request status to resolved
            # as well as logging of the change
            if not unsolicited_result_tag:
                (
                    original_request,
                    request_status_log_obj,
                ) = self._object_instances_for_request_status_change(
                    original_request=original_request,
                    request_id=request_uuid,
                    status=RequestStatus.RESOLVED,
                    status_change_message="Result posted for corresponding request",
                )
                session.add(request_status_log_obj)

            # Commit all additions and refresh
            session.commit()
            session.refresh(db_obj)
            session.refresh(result_status_log_obj)
            session.refresh(link_quantity_result_obj)
            if not unsolicited_result_tag:
                session.refresh(original_request)
                session.refresh(request_status_log_obj)

        return str(db_obj.uuid)

    def get_pending_requests(
        self,
        quantity: Optional[str] = None,
        method: Optional[str] = None,
    ) -> List[RequestInfo]:
        """Return all pending requests."""
        query_inp = (
            select(DbRequest)
            .join(DbLinkQuantityRequest)
            .join(DbQuantity)
            .where(DbRequest.status == RequestStatus.PENDING.value)
        )

        if quantity is not None:
            query_inp = query_inp.where(DbQuantity.quantity == quantity)
        if method is not None:
            query_inp = query_inp.where(DbQuantity.method == method)

        with get_db() as session:
            query_out = session.execute(query_inp).all()

        api_response = []
        for (request_info,) in query_out:
            request_obj = RequestInfo.from_db_request(request_info)
            api_response.append(request_obj)

        return api_response

    def get_all_requests(self) -> List[RequestInfo]:
        """Return all requests."""
        query_inp = select(DbRequest)

        with get_db() as session:
            query_out = session.execute(query_inp).all()

        api_response = []
        for (request_info,) in query_out:
            request_obj = RequestInfo.from_db_request(request_info)
            api_response.append(request_obj)

        return api_response

    def validate_submission(
        self, quantity: str, methods: List[str], parameters: Dict[str, dict]
    ):
        """Validates"""
        query_inp = select(DbQuantity).where(DbQuantity.quantity == quantity)
        with get_db() as session:
            query_out = session.execute(query_inp).all()

        if len(query_out) == 0:
            logger.raise_value_error(
                logger=logger, msg=f"No records for this quantity: {quantity}"
            )

        for method in parameters.keys():
            if method not in methods:
                logger.raise_value_error(
                    logger=logger,
                    msg=(
                        f"Method for params with key {method} not found in list: "
                        f"{methods}"
                    ),
                )

        for method in methods:
            if method not in parameters.keys():
                logger.raise_value_error(
                    logger=logger,
                    msg=f"Method {method} not found in parameters: {parameters.keys()}",
                )

            match_found = False
            specific_params = parameters[method]
            for (quantity_dbobj,) in query_out:
                schema_specs = json.loads(quantity_dbobj.specifications)
                if method == quantity_dbobj.method:
                    validate(instance=specific_params, schema=schema_specs)
                    match_found = True
                    break
            if not match_found:
                logger.raise_value_error(
                    logger=logger, msg=f"No records for this method: {method}"
                )

    def get_result_by_request(self, request_id: str) -> Optional[ResultInfo]:
        """Return the result corresponding to a given request ID."""
        query_inp = select(DbResult).where(
            DbResult.request_uuid == uuid.UUID(request_id)
        )
        with get_db() as session:
            query_out = session.execute(query_inp).all()

        if len(query_out) == 0:
            return None

        api_response = ResultInfo.from_db_result(query_out[0][0])
        return api_response

    def get_all_results(
        self,
        quantity: Optional[str] = None,
        method: Optional[str] = None,
    ) -> List[Result]:
        """Returns all results a given tenant has access to.

        Currently there is no tenant verification so this just returns
        all available results.

        Filtering currently supported only for quantity and method.
        """
        query_inp = select(DbResult).join(DbLinkQuantityResult).join(DbQuantity)
        if quantity is not None:
            query_inp = query_inp.where(DbQuantity.quantity == quantity)
        if method is not None:
            query_inp = query_inp.where(DbQuantity.method == method)

        with get_db() as session:
            query_out = session.execute(query_inp).all()

        api_response = []
        for (result_info,) in query_out:
            result_obj = ResultInfo.from_db_result(result_info)
            api_response.append(result_obj)

        return api_response

    def change_status_request(
        self,
        request_id: str,
        status: RequestStatus,
        status_change_message: Optional[str] = None,
    ) -> str:
        """
        Checks the given status is one of the allowed strings, if so overwrite
        the value in the request table, and log the change in the request status log
        table.
        Passing the same status which is already currently logged, won't result in an
        error, since a new status_change_message can accompany the new log entry for a
        further/new description.
        """

        # return if status change it not allowed
        if status == RequestStatus.RESOLVED or status == RequestStatus.UNSOLICITED:
            logger.raise_value_error(
                logger=logger,
                msg=(
                    f"It is not possible to change the status to {status.value}, "
                    "since this is handled entirely on ther server side"
                ),
            )

        # Change status and log change
        query_inp = select(DbRequest).where(DbRequest.uuid == uuid.UUID(request_id))
        with get_db() as session:
            # Retrieve original request and update request status
            query_out = session.execute(query_inp).all()
            if len(query_out) == 0:
                logger.raise_value_error(
                    logger=logger, msg=f"No request with id: {request_id}"
                )

            original_request = query_out[0][0]

            # Raise error if the status is 'resolved'
            if original_request.status == RequestStatus.RESOLVED:
                logger.raise_value_error(
                    logger=logger,
                    msg=(
                        "The requests is connected to an already posted results and"
                        "therefore has the status 'resolved' which cannot be changed."
                    ),
                )
            if original_request.status == RequestStatus.UNSOLICITED:
                logger.raise_value_error(
                    logger=logger,
                    msg=(
                        "The requests was created to accomadate posting a result "
                        "without a request being present, the status 'unsolicited' can "
                        "therefore not be changed."
                    ),
                )

            # Retrieves the object to be for changing the request status as well as
            # logging of the change
            (
                original_request,
                request_status_log_obj,
            ) = self._object_instances_for_request_status_change(
                original_request, request_id, status, status_change_message
            )

            session.add(request_status_log_obj)
            session.commit()

            session.refresh(request_status_log_obj)
            session.refresh(original_request)

        api_response = f"Successful change of status to {status.value}"
        return api_response

    def change_status_result(
        self,
        result_id: str,
        status: ResultStatus,
        status_change_message: Optional[str] = None,
    ) -> str:
        """
        Checks the given status is one of the allowed strings, if so overwrite
        the value in the result table, and log the change in the result status log
        table.
        Passing the same status which is already currently logged, won't result in an
        error, since a new status_change_message can accompany the new log entry for a
        further/new description.
        """

        # Here it is enforced that it is not possible to change status to 'original'
        # since this is reserved for the status when the data is initially posted
        if status == ResultStatus.ORIGINAL:
            logger.raise_value_error(
                logger=logger,
                msg=(
                    f"Not possible to change status to '{ResultStatus.ORIGINAL.value}' "
                    "since this is reserved only for the initial posting"
                ),
            )

        # Change status and log change
        query_inp = select(DbResult).where(DbResult.uuid == uuid.UUID(result_id))
        with get_db() as session:
            # Retrieve original result and update result status
            query_out = session.execute(query_inp).all()
            if len(query_out) == 0:
                logger.raise_value_error(
                    logger=logger, msg=f"No result with id: {result_id}"
                )
            original_result = query_out[0][0]

            # Update value
            original_result.status = status.value
            result_status_log_obj = DbStatusLogResult(
                **{
                    "uuid": str(uuid.uuid4()),
                    "result_uuid": result_id,
                    "status": status.value,
                    "status_change_message": status_change_message,
                }
            )

            session.add(result_status_log_obj)
            session.commit()
            session.refresh(result_status_log_obj)
            session.refresh(original_result)

        api_response = f"Successful change of status to {status.value}"
        return api_response

    def _object_instances_for_request_status_change(
        self, original_request, request_id, status, status_change_message
    ):
        """
        Function for returning the request and log object to be stored when changing
        status of a request
        """

        # Update value
        original_request.status = status.value

        request_status_log_obj = DbStatusLogRequest(
            **{
                "uuid": str(uuid.uuid4()),
                "request_uuid": request_id,
                "status": status.value,
                "status_change_message": status_change_message,
            }
        )

        return original_request, request_status_log_obj

    def database_dump_key_authentication(self, access_key_user_provided):
        """
        Authenticating the key from the user with the environment variable key.
        The key is not allowed to be the default from the repo, due to secruity aspect.
        Function will return without error if key is authenticated.
        """

        ACCESS_KEY_ENVIRONMENT_VARIABLE = os.environ.get(
            "KEY_DATABASE_DUMP_ENDPOINT_ACCESS"
        )

        # Check that access key exists and is not the default
        # which does not allow access
        if (
            ACCESS_KEY_ENVIRONMENT_VARIABLE is None
            or ACCESS_KEY_ENVIRONMENT_VARIABLE == "DEFAULT_KEY_PLACEHOLDER"
        ):
            logger.raise_value_error(
                logger=logger,
                msg=(
                    "The key for accessing the endpoint has not been initiated "
                    "correctly, contact the server team"
                ),
            )

        # Check that the provided and environment key match
        if access_key_user_provided != ACCESS_KEY_ENVIRONMENT_VARIABLE:
            logger.raise_value_error(
                logger=logger,
                msg=(
                    f"The key {access_key_user_provided} is not a variable present in "
                    "the server instance, access to the database-dump endpoint denied"
                ),
            )

        # Access granted, database is dumped through the API
        return
