import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from jsonschema import validate

from FINALES2.server.schemas import (
    CapabilityInfo,
    Request,
    RequestInfo,
    Result,
    ResultInfo,
)

# -----------------------------------------------------------------------------#
# This is temporary memory storage until I have access to the database
dummy_schema = {
    "type": "object",
    "properties": {
        "temperature": {
            "type": "number",
            "description": (
                "the temperature of the system (this is just a temporary stand in)",
            ),
        }
    },
    "required": ["temperature"],
}

tempdict_requests: Dict[str, Any] = {}
tempdict_results: Dict[str, Any] = {}
tempdict_quantities: Dict[str, Any] = {
    "DummyCapability": CapabilityInfo(
        name="DummyQuantity", method="DummyMethod", json_schema=dummy_schema
    )
}
# -----------------------------------------------------------------------------#


class Engine:
    def get_request(self, object_id: str) -> Optional[Request]:
        """Retrieve a request entry from the database by id."""
        # Temporarily, this just stores the requests in memory
        if object_id in tempdict_requests:
            return tempdict_requests[object_id]
        return None

    def get_result(self, object_id: str) -> Optional[Result]:
        """Retrieve a result entry from the database by id."""
        # Temporarily, this just stores the results in memory
        if object_id in tempdict_results:
            return tempdict_results[object_id]
        return None

    def put_request(self, request_data: Request) -> str:
        """Create a new request entry in the database.

        This method will first validate the parameters of the request with
        the internal schema that corresponds to the quantity + method
        capability.

        When creating the request object, it assigns a new uuid (and returns it).
        """
        # Obviously temporary fake validation, but to test jsonschema.validate
        submitted_params = request_data.parameters
        validate(instance=submitted_params, schema=dummy_schema)

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

    def put_result(self, result_data: Result) -> str:
        """Create a new result entry in the database.

        This method will first validate the parameters of the request with
        the internal schema that corresponds to the quantity + method
        capability.

        When creating the result object, it assigns a new uuid (and returns it).
        """
        # Obviously temporary fake validation, but to test jsonschema.validate
        submitted_params = result_data.parameters
        validate(instance=submitted_params, schema=dummy_schema)

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

    def get_pending_requests(self) -> List[RequestInfo]:
        """Return all pending requests."""
        # Currently it just gets all requests, status check pending
        json_datalist = [result.dict() for result in tempdict_results.values()]
        json_datastr = json.dumps(json_datalist, indent=2, default=str)
        print(
            f"Printing results in the server since we can't currently check"
            f"them with an endpoint:\n {json_datastr}"
        )
        return [value for value in tempdict_requests.values()]

    def get_capabilities(self, currently_available=True) -> List[CapabilityInfo]:
        """Return all (currently available) capabilities."""
        if currently_available:
            print("This should filter based on the available tenants")
        else:
            print("This should show all definitions in the quantity table")
        return [value for value in tempdict_quantities.values()]
