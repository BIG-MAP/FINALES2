import json
import uuid
from typing import Any, Dict, List, Optional

import jsonref
from jsonschema import validate
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

        is_active = 1
        tenant_data = {
            "uuid": str(uuid.uuid4()),
            "name": tenant_specs["name"],
            "limitations": json.dumps(tenant_limitations),
            "capabilities": json.dumps(tenant_specs["capabilities"]),
            "contact_person": tenant_specs["contact_person"],
            "is_active": is_active,
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
        """Return all (currently available) capabilities. currently_available=True will
        return capabilities based on avaliable tenants. currently_available=False will
        show all capabilities defined that are registered in the database."""

        # Filter for the quantities tenants can register for
        query_inp = select(Quantity).where(Quantity.is_active == 1)
        if quantity is not None:
            query_inp = query_inp.where(Quantity.quantity == quantity)
        if method is not None:
            query_inp = query_inp.where(Quantity.method == method)

        with self._database_context() as session:
            query_out = session.execute(query_inp).all()

        # Retrieve all current active tenants
        query_inp_tenant = select(Tenant).where(Tenant.is_active == 1)
        with self._database_context() as session:
            query_out_tenant = session.execute(query_inp_tenant).all()

        # Create a list of all the methods currently provided by active tenants
        active_method_list = []
        for (tenant,) in query_out_tenant:
            tenant_limitations = json.loads(tenant.limitations)
            for limitation in tenant_limitations:
                if limitation["method"] not in active_method_list:
                    active_method_list.append(limitation["method"])

        api_response = []
        for (capability,) in query_out:
            # If currently_available=True we need to also check that the capability is
            # currently being provided by an active tenant in the MAP
            if not currently_available or capability.method in active_method_list:
                new_object = CapabilityInfo.from_db_quantity(capability)
                api_response.append(new_object)

        return api_response

    def get_limitations(self, currently_available=True) -> List[LimitationsInfo]:
        """
        Return all (currently available) limitations. currently_available=True will
        return limitations based on avaliable tenants. currently_available=False will
        show all limtations defined that are registered in the database.
        """

        query_inp = select(Tenant)
        # Filters for all currently available tenants
        if currently_available:
            query_inp = query_inp.where(Tenant.is_active == 1)

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

        capability_schema = capability_info[0].json_schema_specifications
        capability_schema = jsonref.replace_refs(capability_schema)
        limitations_schema = limitations_schema_translation(capability_schema)
        limitations = limitations["limitations"]
        validate(instance=limitations, schema=limitations_schema)

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


def limitations_schema_translation(inputs_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates the limitations schema in a recursive way from parameters schema.
    """

    # Trivial case: if there are no parameters, there can be no limitations.
    if len(inputs_schema) == 0:
        return {"additionalProperties": False}

    # Every object in the schema becomes an array of objects with the
    # possible values (or ranges).
    limitations_schema: Dict[str, Any] = {"type": "array"}

    # The title is not necessary but may be useful for debugging at runtime
    if "title" in inputs_schema:
        limitations_schema["title"] = inputs_schema["title"]

    # Now I need to set the "items" descriptor of the array, which contains
    # the type of the objects in it.

    if "anyOf" in inputs_schema:
        # If the object could have many types, it will not have a "type"
        # descriptor but an "anyOf" list of descriptors. I need to go
        # through all of them and add them as an "anyOf" in the "items".
        limitations_schema["items"] = {"anyOf": []}
        for schema_item in inputs_schema["anyOf"]:
            new_schema = limitations_schema_translation(schema_item)
            limitations_schema["items"]["anyOf"].append(new_schema)

    elif inputs_schema["type"] in ["number", "integer"]:
        # If the object was a numeric type, the type of the possibilities
        # in the array will be of either that same numeric type, or a dict
        # defining a possible range.
        number_type = inputs_schema["type"]
        cases_schema = {"type": number_type}
        range_schema = {
            "type": "object",
            "properties": {
                "min": {"type": number_type},
                "max": {"type": number_type},
                "step": {"type": number_type},
            },
            "additionalProperties": False,
        }
        limitations_schema["items"] = {"anyOf": [range_schema, cases_schema]}

    elif inputs_schema["type"] == "array":
        # If the object was an array, the type is defined inside of "items".
        new_items = inputs_schema["items"]
        new_items = limitations_schema_translation(new_items)
        limitations_schema["items"] = new_items

    else:
        # If the object was a string or any other, the type is defined
        # inside of "type". If it was a string then this is over, but
        # if it was another custom type, I need to go throught its
        # properties and add them recursively.
        limitations_schema["items"] = {"type": inputs_schema["type"]}

        if "properties" in inputs_schema:
            limitations_schema["items"]["properties"] = {}
            for propery_name, property_schema in inputs_schema["properties"].items():
                new_property = limitations_schema_translation(property_schema)
                limitations_schema["items"]["properties"][propery_name] = new_property

        if "additionalProperties" in inputs_schema:
            new_property = inputs_schema["additionalProperties"]
            new_property = limitations_schema_translation(new_property)
            limitations_schema["items"]["additionalProperties"] = new_property

    return limitations_schema
