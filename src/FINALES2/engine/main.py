import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from jsonschema import validate
from sqlalchemy import select

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

        # Getting the methods and quantity from the uuid
        methods_uuid_str = json.loads(query_out[0][0].methods_uuid)
        methods_uuid = [uuid.UUID(entry) for entry in methods_uuid_str]
        query_inp_method_retrieval = select(DbQuantity).where(
            DbQuantity.uuid.in_(methods_uuid)
        )
        with get_db() as session:
            query_out_method_retrieval = session.execute(
                query_inp_method_retrieval
            ).all()

        quantity = query_out_method_retrieval[0][0].quantity
        methods = []
        for (methods_iter,) in query_out_method_retrieval:
            methods.append(methods_iter.method)

        api_response = Request.from_db_request(
            query_out[0][0], quantity, json.dumps(methods)
        )
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

        # Retrieving the uuid from the quantity table for the specific method
        quantity = request_data.quantity
        method = request_data.methods[0]
        query_inp = select(DbQuantity.uuid).where(
            DbQuantity.method == method, DbQuantity.quantity == quantity
        )
        with get_db() as session:
            query_out = session.execute(query_inp).all()

        methods_uuid = []
        for (method_uuid,) in query_out:
            methods_uuid.append(str(method_uuid))

        request_obj = DbRequest(
            **{
                "uuid": str(uuid.uuid4()),
                "methods_uuid": json.dumps(methods_uuid),
                "parameters": json.dumps(request_data.parameters),
                "requesting_tenant_uuid": str(uuid.uuid4()),  # get from auth metadata
                "requesting_recieved_timestamp": ctime,
                "budget": "not currently implemented in the API",
                "status": json.dumps(
                    [(ctime, RequestStatus.PENDING.value)], default=str
                ),
            }
        )

        with get_db() as session:
            session.add(request_obj)
            session.commit()
            session.refresh(request_obj)

        return str(request_obj.uuid)

    def create_result(self, received_data: Result) -> str:
        """Create a new result entry in the database.

        This method will first validate the parameters of the request with
        the internal schema that corresponds to the quantity + method
        capability.

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

        db_obj = DbResult(
            **{
                "uuid": str(uuid.uuid4()),
                "request_uuid": request_uuid,  # get from received data and check
                "quantity": received_data.quantity,
                "method": json.dumps(received_data.method),
                "parameters": json.dumps(received_data.parameters),
                "data": json.dumps(received_data.data),
                "posting_tenant_uuid": str(uuid.uuid4()),  # get from auth metadata
                "cost": "Not implemented in the API yet",
                "status": "Not implemented in the API yet",
                "posting_recieved_timestamp": ctime,
            }
        )

        with get_db() as session:
            query_out = session.execute(query_inp).all()
            if len(query_out) == 0:
                raise ValueError(f"Submitted result has no request: {request_uuid}")
            original_request = query_out[0][0]
            status_list = json.loads(original_request.status)
            status_list.append((ctime, RequestStatus.RESOLVED.value))
            original_request.status = json.dumps(status_list, default=str)
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            session.refresh(original_request)

        return str(db_obj.uuid)

    def get_pending_requests(self) -> List[RequestInfo]:
        """Return all pending requests."""
        # Starts by retrieving all uuid from the quantities for retireving methods and
        # quantities
        query_inp_quantity = select(DbQuantity)

        with get_db() as session:
            query_out_quantity = session.execute(query_inp_quantity).all()

        quantity_dict = {}
        for (quantity_entry,) in query_out_quantity:
            quantity_dict[str(quantity_entry.uuid)] = [
                quantity_entry.quantity,
                quantity_entry.method,
            ]

        # Currently it just gets all requests, status check pending
        query_inp = select(DbRequest).where(
            DbRequest.status.like('%"' + RequestStatus.PENDING.value + '"]]')
        )

        with get_db() as session:
            query_out = session.execute(query_inp).all()

        api_response = []
        for (request_info,) in query_out:
            methods_uuid = json.loads(request_info.methods_uuid)
            methods = []
            for method_uuid in methods_uuid:
                quantity, method = quantity_dict[method_uuid]
                methods.append(method)

            request_obj = RequestInfo.from_db_request(
                request_info, quantity, json.dumps(methods)
            )
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
        query_inp = select(DbResult)
        if quantity is not None:
            query_inp = query_inp.where(DbResult.quantity == quantity)
        if method is not None:
            # NOTE: Currently method is stored as a string which contains a list
            # with a single method. We should really consider having method be
            # a single string in this case; but more in general this shows a big
            # disadvantage of storing potentially queryable list/dict fields as
            # serialized strings.
            query_inp = query_inp.where(DbResult.method == f'["{method}"]')

        with get_db() as session:
            query_out = session.execute(query_inp).all()

        api_response = []
        for (result_info,) in query_out:
            result_obj = Result.from_db_result(result_info)
            api_response.append(result_obj)

        return api_response
