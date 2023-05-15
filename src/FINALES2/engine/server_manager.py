import json
import uuid
from typing import List, Optional

from sqlalchemy import select

from FINALES2.db import Quantity, Tenant
from FINALES2.server.schemas import CapabilityInfo


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
