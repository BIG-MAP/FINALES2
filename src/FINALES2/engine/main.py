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
from FINALES2.db.session import get_db
from FINALES2.server.schemas import CapabilityInfo, Request, RequestInfo, Result


class RequestStatus(Enum):
    PENDING = "pending"
    RESERVED = "reserved"
    RESOLVED = "resolved"
    RETRACTED = "retracted"


class Engine:
    """This class is the outermost manager of the functionalities of finales."""

    def get_request(self, object_id: str) -> Optional[Request]:
        """Retrieve a request entry from the database by id."""
        query_inp = select(DbRequest).where(DbRequest.uuid == uuid.UUID(object_id))
        with get_db() as session:
            query_out = session.execute(query_inp).all()

        if len(query_out) == 0:
            return None

        api_response = Request.from_db_request(query_out[0][0])
        return api_response

    def get_result(self, object_id: str) -> Optional[Result]:
        """Retrieve a result entry from the database by id."""
        query_inp = select(DbResult).where(DbResult.uuid == uuid.UUID(object_id))
        with get_db() as session:
            query_out = session.execute(query_inp).all()

        if len(query_out) == 0:
            return None
        api_response = Result.from_db_result(query_out[0][0])
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
                "status": json.dumps(
                    [(ctime, RequestStatus.PENDING.value)], default=str
                ),
            }
        )

        link_uuid = str(uuid.uuid4())
        with get_db() as session:
            # Add the request to the session
            session.add(request_obj)

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
                # "quantity": received_data.quantity,
                # "method": json.dumps(received_data.method),
                "parameters": json.dumps(received_data.parameters),
                "data": json.dumps(received_data.data),
                "posting_tenant_uuid": str(uuid.uuid4()),  # get from auth metadata
                "cost": "Not implemented in the API yet",
                "status": "Not implemented in the API yet",
                "posting_recieved_timestamp": ctime,
            }
        )

        with get_db() as session:
            # Retrieve original request for the result and update request status
            query_out = session.execute(query_inp).all()
            if len(query_out) == 0:
                raise ValueError(f"Submitted result has no request: {request_uuid}")
            original_request = query_out[0][0]
            status_list = json.loads(original_request.status)
            status_list.append((ctime, RequestStatus.RESOLVED.value))
            original_request.status = json.dumps(status_list, default=str)
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

    def get_pending_requests(self) -> List[RequestInfo]:
        """Return all pending requests."""
        # Currently it just gets all requests, status check pending
        query_inp = select(DbRequest).where(
            DbRequest.status.like('%"' + RequestStatus.PENDING.value + '"]]')
        )

        with get_db() as session:
            query_out = session.execute(query_inp).all()

        api_response = []
        for (request_info,) in query_out:
            request_obj = RequestInfo.from_db_request(request_info)
            api_response.append(request_obj)

        return api_response

    def get_capabilities(self, currently_available=True) -> List[CapabilityInfo]:
        """Return all (currently available) capabilities."""
        if currently_available:
            print("This should filter based on the available tenants")
        else:
            print("This should show all definitions in the quantity table")

        query_inp = select(DbQuantity)  # .where()
        with get_db() as session:
            query_out = session.execute(query_inp).all()

        api_response = []
        for (capability,) in query_out:
            new_object = CapabilityInfo.from_db_quantity(capability)
            api_response.append(new_object)

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

    def get_result_by_request(self, request_id: str) -> Optional[Result]:
        """Return the result corresponding to a given request ID."""
        query_inp = select(DbResult).where(
            DbResult.request_uuid == uuid.UUID(request_id)
        )
        with get_db() as session:
            query_out = session.execute(query_inp).all()

        if len(query_out) == 0:
            return None

        api_response = Result.from_db_result(query_out[0][0])
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
            # NOTE: Currently method is stored as a string which contains a list
            # with a single method. We should really consider having method be
            # a single string in this case; but more in general this shows a big
            # disadvantage of storing potentially queryable list/dict fields as
            # serialized strings.
            query_inp = query_inp.where(DbQuantity.method == method)

        with get_db() as session:
            query_out = session.execute(query_inp).all()

        api_response = []
        for (result_info,) in query_out:
            result_obj = Result.from_db_result(result_info)
            api_response.append(result_obj)

        return api_response
