import json
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


class RequestStatus(Enum):
    PENDING = "pending"
    RESERVED = "reserved"
    RESOLVED = "resolved"
    RETRACTED = "retracted"


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

    def create_request(self, request_data: Request) -> str:
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
                "requesting_tenant_uuid": str(uuid.uuid4()),  # get from auth metadata
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
                    raise ValueError(
                        f"The method {method_name} for quantity {request_data.quantity}"
                        f" has several entries ({len(query_out)}) in the quantity table"
                        f" which are active"
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

    def create_result(self, received_data: Result) -> str:
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
            raise ValueError(
                "Wrong length of method string for recieved result. "
                "A list with a single method is expected, the recieved list "
                f"{received_data.method} does not comply with this"
            )
        if len(received_data.parameters) != 1:
            raise ValueError(
                "Wrong number of keys in passed parameters. A single key with the "
                "specific method was expected, the recieved parameters has the "
                f"following keys {list(received_data.parameters.keys())} and does not "
                "comply with this"
            )

        method_name = received_data.method[0]
        wrapped_params = {method_name: received_data.parameters[method_name]}
        self.validate_submission(
            received_data.quantity, received_data.method, wrapped_params
        )

        request_uuid = str(received_data.request_uuid)
        query_inp = select(DbRequest).where(DbRequest.uuid == request_uuid)

        ctime = datetime.now()

        result_uuid = str(uuid.uuid4())
        db_obj = DbResult(
            **{
                "uuid": result_uuid,
                "request_uuid": request_uuid,  # get from received data and check
                "parameters": json.dumps(received_data.parameters),
                "data": json.dumps(received_data.data),
                "posting_tenant_uuid": str(uuid.uuid4()),  # get from auth metadata
                "cost": "Not implemented in the API yet",
                "status": ResultStatus.ORIGINAL.value,
                "posting_recieved_timestamp": ctime,
            }
        )

        with get_db() as session:
            # Retrieve original request for the result and update request status
            query_out = session.execute(query_inp).all()
            if len(query_out) == 0:
                raise ValueError(f"Submitted result has no request: {request_uuid}")

            original_request = query_out[0][0]
            original_request.status = RequestStatus.RESOLVED.value
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
                raise ValueError(
                    f"The method {method_name} for quantity {received_data.quantity} "
                    f"has several entries ({len(query_out_method)}) in the quantity "
                    f"table which are active"
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

            # Commit all additions and refresh
            session.commit()
            session.refresh(db_obj)
            session.refresh(original_request)
            session.refresh(link_quantity_result_obj)

        return str(db_obj.uuid)

    def get_pending_requests(
        self,
        quantity: Optional[str] = None,
        method: Optional[str] = None,
    ) -> List[RequestInfo]:
        """Return all pending requests."""
        # Currently it just gets all requests, status check pending
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

    def validate_submission(
        self, quantity: str, methods: List[str], parameters: Dict[str, dict]
    ):
        """Validates"""
        query_inp = select(DbQuantity).where(DbQuantity.quantity == quantity)
        with get_db() as session:
            query_out = session.execute(query_inp).all()

        if len(query_out) == 0:
            raise ValueError(f"No records for this quantity: {quantity}")

        for method in parameters.keys():
            if method not in methods:
                raise ValueError(
                    f"Method for params with key {method} not found in list: {methods}"
                )

        for method in methods:
            if method not in parameters.keys():
                raise ValueError(
                    f"Method {method} not found in parameters: {parameters.keys()}"
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
                raise ValueError(f"No records for this method: {method}")

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

    def change_status_request(self, request_id, status, status_change_message):
        """
        Checks the given status is one of the allowed strings, if so overwrite
        the value in the request table, and log the change in the request status log
        table
        """

        # Check if result is already associated with request.
        # This logic also infer that a status "resolved" cannot be changed
        query_inp_result = select(DbResult.status).where(
            DbResult.request_uuid == uuid.UUID(request_id)
        )
        with get_db() as session:
            query_out_result = session.execute(query_inp_result).all()
            if len(query_out_result) != 0:
                raise ValueError(
                    f"Cannot change status of request to '{status}' since an associated"
                    f" result with status '{query_out_result[0][0]}' is already posted"
                )

        # Change status and log change
        query_inp = select(DbRequest).where(DbRequest.uuid == uuid.UUID(request_id))
        with get_db() as session:
            # Retrieve original request and update request status
            query_out = session.execute(query_inp).all()
            if len(query_out) == 0:
                raise ValueError(f"No request with id: {request_id}")

            original_request = query_out[0][0]
            # Update value
            original_request.status = status

            request_status_log_obj = DbStatusLogRequest(
                **{
                    "uuid": str(uuid.uuid4()),
                    "request_uuid": request_id,
                    "status": status,
                    "status_change_message": status_change_message,
                }
            )
            session.add(request_status_log_obj)
            session.commit()

            session.refresh(request_status_log_obj)
            session.refresh(original_request)

        api_response = f"Successful change of status to {status}"
        return api_response

    def change_status_result(self, result_id, status, status_change_message):
        """
        Checks the given status is one of the allowed strings, if so overwrite
        the value in the result table, and log the change in the result status log
        table
        """

        # Not possible to change status to 'original'
        if status == ResultStatus.ORIGINAL.value:
            ValueError(
                f"Not possible to change status to '{ResultStatus.ORIGINAL.value}' "
                "since this is reserved only for the initial posting"
            )

        # Change status and log change
        query_inp = select(DbResult).where(DbResult.uuid == uuid.UUID(result_id))
        with get_db() as session:
            # Retrieve original result and update result status
            query_out = session.execute(query_inp).all()
            if len(query_out) == 0:
                raise ValueError(f"No result with id: {result_id}")

            original_request = query_out[0][0]
            # Update value
            original_request.status = status

            result_status_log_obj = DbStatusLogResult(
                **{
                    "uuid": str(uuid.uuid4()),
                    "request_uuid": result_id,
                    "status": status,
                    "status_change_message": status_change_message,
                }
            )
            session.add(result_status_log_obj)
            session.commit()

            session.refresh(result_status_log_obj)
            session.refresh(original_request)

        api_response = f"Successful change of status to {status}"
        return api_response
