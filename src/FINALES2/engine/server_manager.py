import json
import uuid
from typing import Any, Dict, List, Optional

import jsonschema
import jsonsubschema
from sqlalchemy import select

from FINALES2.db import Quantity, Tenant
from FINALES2.server.schemas import CapabilityInfo, LimitationsInfo


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

        # Check if entry already exists in database
        self._dublicate_capability_db_check(new_capability)

        with self._database_context() as session:
            session.add(new_capability)
            session.commit()
            session.refresh(new_capability)

    def add_tenant(self, tenant_specs):
        """Adds new tenant to the server."""
        tenant_limitations = tenant_specs["limitations"]
        for limitations in tenant_limitations:
            self.validate_limitations(limitations)

        tenant_data = {
            "uuid": str(uuid.uuid4()),
            "name": tenant_specs["name"],
            "limitations": json.dumps(tenant_limitations),
            "capabilities": json.dumps(tenant_specs["capabilities"]),
            "contact_person": tenant_specs["contact_person"],
        }
        new_tenant = Tenant(**tenant_data)

        # Check if entry already exists in database
        self._dublicate_tenant_db_check(new_tenant)

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

        query_inp = select(Quantity)
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

        query_inp = select(Tenant)
        with self._database_context() as session:
            query_out = session.execute(query_inp).all()

        # Internally, the entries of the tables contains the limitations for
        # the capabilities (quantity/method combinations) of each tenant.
        #     {
        #       Tenant1: { Capability1: lims, Capability2: lims, ... },
        #       Tenant2: { Capability2: lims, Capability3: lims, ... },
        #       ...
        #     }
        #
        # But for reporting back, it is better to group all limitations of
        # the different tenants that provide a given capability together:
        #     {
        #       Capability1: lims (aggregated from tenants with Capability1),
        #       Capability2: lims (aggregated from tenants with Capability2),
        #       ...
        #     }
        limitations_accumdict: Dict[str, Any] = {}
        for (tenant,) in query_out:
            limitations_datalist = json.loads(tenant.limitations)
            for limitations_data in limitations_datalist:
                quantity = limitations_data["quantity"]
                if quantity not in limitations_accumdict:
                    limitations_accumdict[quantity] = {}

                method = limitations_data["method"]
                if method not in limitations_accumdict[quantity]:
                    limitations_accumdict[quantity][method] = []

                limitations_schema = limitations_data["limitations"]
                limitations_accumdict[quantity][method].append(limitations_schema)

        api_response = []
        for keyq, limitations_methods in limitations_accumdict.items():
            for keym, limitations_schemas in limitations_methods.items():
                api_response.append(
                    LimitationsInfo(
                        quantity=keyq,
                        method=keym,
                        limitations={"anyOf": limitations_schemas},
                    )
                )

        return api_response

    def validate_limitations(self, limitations: LimitationsInfo):
        """Validates a set of limitations."""

        capability_info = self.get_capabilities(
            quantity=limitations["quantity"],
            method=limitations["method"],
            currently_available=False,
        )

        if len(capability_info) == 0:
            raise ValueError(
                f"The quantity ({limitations['quantity']}) and method "
                f"({limitations['method']}) are not currently present in the "
                "capabilities and the tenant can therefore not be added"
            )

        limitations_superschema = capability_info[0].json_schema_specifications
        limitations_subschema = limitations["limitations"]

        is_subschema = jsonsubschema.isSubschema(
            limitations_subschema, limitations_superschema
        )
        if not is_subschema:
            raise jsonschema.exceptions.ValidationError(
                "Limitations are not a subschema"
            )

    def _dublicate_capability_db_check(self, db_entry):
        """
        Method for checking if the method being added to the capabilities is already
        present in the database with status active
        """

        active_entry = True
        query_inp = (
            select(Quantity)
            .where(Quantity.quantity == db_entry.quantity)
            .where(Quantity.method == db_entry.method)
            .where(active_entry == db_entry.is_active)
        )

        with self._database_context() as session:
            query_out = session.execute(query_inp).all()

        if len(query_out) > 0:
            raise ValueError(
                f"The quantity ({db_entry.quantity}) method ({db_entry.method}) is "
                "already present in the database with same is_active state "
                f"({db_entry.is_active})"
            )

        return

    def _dublicate_tenant_db_check(self, db_entry):
        """
        Method for checking if the method being added to the capabilities is already
        present in the database with status active
        """

        # TODO currently no is_active approach to the tenant
        query_inp = (
            select(Tenant)
            .where(Tenant.name == db_entry.name)
            .where(Tenant.limitations == db_entry.limitations)
            .where(Tenant.capabilities == db_entry.capabilities)
        )

        with self._database_context() as session:
            query_out = session.execute(query_inp).all()

        if len(query_out) > 0:
            raise ValueError(
                f"The tenant ({db_entry.name}) is already present in the database with "
                "identical limitations and capabilities"
            )

        return
