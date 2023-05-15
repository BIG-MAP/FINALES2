import json
import uuid
from typing import Any, Dict, List, Optional

import jsonschema
from sqlalchemy import select

from FINALES2.db import Quantity, Tenant
from FINALES2.engine.limitations_cache import LimitationsCache
from FINALES2.server.schemas import CapabilityInfo, LimitationsInfo

LIMITATION_SCHEMA_OPTIONS = {
    "type": "object",
    "properties": {
        "available_options": {"type": "array", "items": {"type": ["number", "string"]}}
    },
}

LIMITATION_SCHEMA_RANGE = {
    "type": "object",
    "properties": {
        "available_range": {
            "type": "array",
            "minItems": 3,
            "maxItems": 3,
            "items": {"type": "number"},
        }
    },
}


class ServerManager:
    """Class to manage the general aspects of the server."""

    def __init__(self, database_context):
        """Initializes the server manager."""
        self._database_context = database_context

    def add_capability(self, capability_specs):
        """Adds new capability to the server."""

        capability_data = {
            "uuid": str(uuid.uuid4()),
            "quantity": capability_specs["quantity"],
            "method": capability_specs["method"],
            "specifications": json.dumps(
                capability_specs["json_schema_specifications"],
            ),
            "result_output": json.dumps(
                capability_specs["json_schema_result_output"],
            ),
            "is_active": capability_specs["is_active"],
        }
        new_capability = Quantity(**capability_data)

        with self._database_context() as session:
            session.add(new_capability)
            session.commit()
            session.refresh(new_capability)

    def add_tenant(self, tenant_specs):
        """Adds new tenant to the server."""

        tenant_limitations = json.dumps(tenant_specs["limitations"])
        for limitations in tenant_limitations:
            self.validate_limitations(limitations)

        tenant_data = {
            "uuid": str(uuid.uuid4()),
            "name": tenant_specs["name"],
            "limitations": tenant_limitations,
            "capabilities": json.dumps(tenant_specs["capabilities"]),
            "contact_person": tenant_specs["contact_person"],
        }
        new_tenant = Tenant(**tenant_data)

        with self._database_context() as session:
            session.add(new_tenant)
            session.commit()
            session.refresh(new_tenant)

    def get_capabilities(
        self,
        quantity: Optional[str] = None,
        method: Optional[str] = None,
        currently_available=True,
    ) -> List[CapabilityInfo]:
        """Return all (currently available) capabilities."""

        if currently_available:
            print("This should filter based on the available tenants")
        else:
            print("This should show all definitions in the quantity table")

        query_inp = select(Quantity)  # .where()
        if quantity is not None:
            query_inp = query_inp.where(Quantity.quantity == quantity)
        if method is not None:
            query_inp = query_inp.where(Quantity.method == method)

        with self._database_context() as session:
            query_out = session.execute(query_inp).all()

        api_response = []
        for (capability,) in query_out:
            new_object = CapabilityInfo.from_db_quantity(capability)
            api_response.append(new_object)

        return api_response

    def get_limitations(self, currently_available=True) -> List[LimitationsInfo]:
        """Return all (currently available) limitations."""

        if currently_available:
            print("This should filter based on the available tenants")
        else:
            print("This should show all definitions in the quantity table")

        query_inp = select(Tenant)  # .where()
        with self._database_context() as session:
            query_out = session.execute(query_inp).all()

        limitations_cache = LimitationsCache()
        for (tenant,) in query_out:
            tenant_limitations = json.loads(tenant.limitations)
            for limitations_item in tenant_limitations:
                self.validate_limitations(limitations_item)
                limitations_cache.add_limitations(limitations_item)

        api_response = limitations_cache.get_limitations()
        return api_response

    def validate_limitations(self, limitations: Dict[str, Any]):
        """Validates a set of limitations."""

        quantity = limitations["quantity"]
        method = limitations["method"]
        limitations_properties = limitations["properties"]

        capability_info = self.get_capabilities(
            quantity=quantity,
            method=method,
            currently_available=False,
        )
        schema_source = capability_info[0].json_schema_specifications
        limitations_schema = self._construct_validator_recursively(schema_source)
        print("\n\n\n\nVALIDATING\n")
        print(limitations_schema)
        print(limitations_properties)
        try:
            jsonschema.validate(
                instance=limitations_properties, schema=limitations_schema
            )
            print("VALID!\n\n\n")
        except jsonschema.exceptions.ValidationError as error:
            print("\n\n")
            print(error)
            print("\nOOPSIE\n\n\n")

    def _construct_validator_recursively(self, schema_source):
        """Constructs the schema to validate the limitations recursively."""

        output_schema = {}
        for key, val in schema_source.items():
            if key == "type" and val == "string":
                return LIMITATION_SCHEMA_OPTIONS

            if key == "type" and val == "number":
                return LIMITATION_SCHEMA_RANGE

            if isinstance(val, dict):
                output_schema[key] = self._construct_validator_recursively(val)

            else:
                output_schema[key] = val

        return output_schema
