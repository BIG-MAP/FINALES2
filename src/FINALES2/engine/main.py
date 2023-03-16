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
        api_response = Request(
            quantity=db_request.quantity,
            methods="Currently not implemented in DB.",
            parameters={"info": "Currently not implemented in DB."},
            tenant_uuid=str(db_request.tenant_uuid),
        )
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

        api_response = Result(
            data=json.loads(db_result.data),
            quantity=db_result.quantity,
            method="Currently not implemented in DB.",
            parameters=json.loads(db_result.parameters),
            tenant_uuid=str(db_result.posting_tenant_uuid),
            request_uuid=str(db_result.request_uuid),
        )
        return api_response

    def put_request(self, request_data: Request) -> str:
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
                "tenant_uuid": str(uuid.uuid4()),  # get from auth metadata
                "load_time": datetime.now(),  # temporary until update DB stuff
            }
        )

        with get_db() as session:
            session.add(request_obj)
            session.commit()
            session.refresh(request_obj)

        return str(request_obj.uuid)

    def put_result(self, received_data: Result) -> str:
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
            print("hellooooo")
            request_obj = Request(
                quantity=request_info.quantity,
                methods="standin...",
                parameters={"info": "still not implemented"},
                tenant_uuid=str(request_info.tenant_uuid),
            )
            request_info = RequestInfo(
                uuid=str(request_info.uuid),
                ctime=request_info.load_time,
                status="not implemented yet",
                request=request_obj,
            )
            api_response.append(request_info)

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
            new_object = CapabilityInfo(
                quantity=capability.quantity,
                method="This is not on the DB yet",
                json_schema=json.loads(capability.specifications),
            )
            api_response.append(new_object)

        return api_response
