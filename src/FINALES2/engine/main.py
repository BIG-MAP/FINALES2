import json
import uuid
from datetime import datetime
from typing import List, Optional

from jsonschema import validate
from sqlalchemy import select

from FINALES2.db import Quantity as DbQuantity
from FINALES2.db import Request as DbRequest
from FINALES2.db import Result as DbResult
from FINALES2.db.session import get_db
from FINALES2.server.schemas import CapabilityInfo, Request, RequestInfo, Result


class Engine:
    def get_request(self, object_id: str) -> Optional[Request]:
        """Retrieve a request entry from the database by id."""
        # Temporarily, this just stores the requests in memory
        query_inp = select(DbRequest).where(DbRequest.uuid == uuid.UUID(object_id))
        with get_db() as session:
            query_out = session.execute(query_inp).all()

        if len(query_out) == 0:
            return None

        db_request = query_out[0][0]
        api_response = Request.from_db_request(db_request)
        return api_response

    def get_result(self, object_id: str) -> Optional[Result]:
        """Retrieve a result entry from the database by id."""
        # Temporarily, this just stores the results in memory
        query_inp = select(DbResult).where(DbResult.uuid == uuid.UUID(object_id))
        with get_db() as session:
            query_out = session.execute(query_inp).all()

        if len(query_out) == 0:
            return None

        db_result = query_out[0][0]

        api_response = Result.from_db_result(db_result)
        return api_response

    def create_request(self, request_data: Request) -> str:
        """Create a new request entry in the database.

        This method will first validate the parameters of the request with
        the internal schema that corresponds to the quantity + method
        capability.

        When creating the request object, it assigns a new uuid (and returns it).
        """
        # Obviously temporary fake validation, but to test jsonschema.validate
        query_inp = select(DbQuantity).where(
            DbQuantity.quantity == request_data.quantity
        )
        with get_db() as session:
            query_out = session.execute(query_inp).all()

        if len(query_out) == 0:
            raise ValueError(f"No records for this quantity: {request_data.quantity}")

        dummy_schema = json.loads(query_out[0][0].specifications)
        submitted_params = request_data.parameters
        validate(instance=submitted_params, schema=dummy_schema)

        request_obj = DbRequest(
            **{
                "uuid": str(uuid.uuid4()),
                "quantity": request_data.quantity,
                "method": request_data.methods,
                "parameters": json.dumps(request_data.parameters),
                "requesting_tenant_uuid": str(uuid.uuid4()),  # get from auth metadata
                "requesting_recieved_timestamp": datetime.now(),
                "budget": "not currently implemented in the API",
                "status": "not currently implemented in the API",
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
        # Obviously temporary fake validation, but to test jsonschema.validate
        query_inp = select(DbQuantity).where(
            DbQuantity.quantity == received_data.quantity
        )
        with get_db() as session:
            query_out = session.execute(query_inp).all()

        if len(query_out) == 0:
            raise ValueError(f"No records for this quantity: {received_data.quantity}")

        dummy_schema = json.loads(query_out[0][0].specifications)
        submitted_params = received_data.parameters
        validate(instance=submitted_params, schema=dummy_schema)

        dbobj = DbResult(
            **{
                "data": json.dumps(received_data.data),
                "uuid": str(uuid.uuid4()),
                "request_uuid": str(uuid.uuid4()),  # get from received data and check
                "quantity": received_data.quantity,
                "parameters": json.dumps(received_data.parameters),
                "posting_tenant_uuid": str(uuid.uuid4()),  # get from auth metadata
                "load_time": datetime.now(),
            }
        )

        with get_db() as session:
            session.add(dbobj)
            session.commit()
            session.refresh(dbobj)

        return str(dbobj.uuid)

    def get_pending_requests(self) -> List[RequestInfo]:
        """Return all pending requests."""
        # Currently it just gets all requests, status check pending
        query_inp = select(DbRequest)  # .where(status is pending)
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
