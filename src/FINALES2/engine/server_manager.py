import json
import uuid
from typing import Any, Dict, List, Optional

from jsonref import JsonRef
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
        currently_available: bool = True,
    ) -> List[CapabilityInfo]:
        """Return all (currently available) capabilities.

        :type currently_available: bool
        :param currently_available: A flag to decide if the capabilities returned are
            from all registered tenants (if False) or only currently available ones
            (if True).
        """

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

    def get_limitations(
        self, currently_available: bool = True
    ) -> List[LimitationsInfo]:
        """
        Return all (currently available) limitations.

        :type currently_available: bool
        :param currently_available: A flag to decide if the limitations returned are
            from all tenants registered in the database (if False) or from avaliable
            tenants that are currently active (if True)
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
                if isinstance(limitations_schema, list):
                    limitations_accumdict[quantity][method].extend(limitations_schema)
                else:
                    limitations_accumdict[quantity][method].append(limitations_schema)

        api_response = []
        for keyq, limitations_methods in limitations_accumdict.items():
            for keym, limitations in limitations_methods.items():
                api_response.append(
                    LimitationsInfo(
                        quantity=keyq,
                        method=keym,
                        limitations=limitations,
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
        capability_schema = JsonRef.replace_refs(capability_schema)
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
            .where(Quantity.is_active == active_entry)
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
        Method for checking if a tenant with the same name and limitations is already
        present in the database with status active
        """

        # TODO currently no is_active approach to the tenant
        query_inp = (
            select(Tenant)
            .where(Tenant.name == db_entry.name)
            .where(Tenant.limitations == db_entry.limitations)
        )

        with self._database_context() as session:
            query_out = session.execute(query_inp).all()

        if len(query_out) > 0:
            raise ValueError(
                f"The tenant ({db_entry.name}) is already present in the database with "
                "identical limitations and capabilities"
            )

        return

    def deactivate_capability(self, method_name):
        """Deactivate the is_active column for a capability."""
        query_inp = (
            select(Quantity)
            .where(Quantity.method == method_name)
            .where(Quantity.is_active == 1)
        )

        with self._database_context() as session:
            query_out = session.execute(query_inp).all()

            if len(query_out) == 0:
                raise ValueError(
                    "No method with this name is currently active in the map"
                )

            capability = query_out[0][0]
            # Updating the is_active column
            capability.is_active = 0

            session.commit()
            session.refresh(capability)

        print(f"The method {method_name} has been deactivated in the map")
        return

    def alter_tenant_state(self, tenant_uuid, new_is_active_state):
        """Adds new state to a tenant."""
        query_inp = select(Tenant).where(Tenant.uuid == uuid.UUID(tenant_uuid))

        with self._database_context() as session:
            query_out = session.execute(query_inp).all()

            if len(query_out) == 0:
                raise ValueError("No tenant exists with the provided uuid")

            tenant = query_out[0][0]
            if tenant.is_active == new_is_active_state:
                raise ValueError(
                    "The capability entry already has the desired is_active state "
                    f"({new_is_active_state})"
                )

            # Updating the is_active column
            tenant.status = new_is_active_state

            session.commit()
            session.refresh(tenant)

        print(
            f"The is_active state of tenant with uuid ({uuid}) was successfully "
            f"changed to ({new_is_active_state})"
        )
        return

    def retrieve_tenant_uuid(self, tenant_name):
        """Retrive uuid from tenant with provided tenant_name. If tenant_name is None
        provide all tenant names with corresponding uuid"""
        query_inp = select(Tenant)
        if tenant_name is not None:
            query_inp = query_inp.where(Tenant.name == tenant_name)

        with self._database_context() as session:
            query_out = session.execute(query_inp).all()

            if len(query_out) == 0:
                if tenant_name is None:
                    raise ValueError(
                        f"No tenant exists with the provided name ({tenant_name})"
                    )
                else:
                    raise ValueError("No tenants in the database")

        for (tenant,) in query_out:
            print(f"tenant: {tenant.name}, uuid: {tenant.uuid}")

        return

    def get_schema_template(
        self,
        quantity: Optional[str] = None,
        method: Optional[str] = None,
        currently_available: bool = True,
    ) -> Dict[str, Dict[str, Any]]:
        """Generates a dictionary, which may be copy-pasted to code and filled with the
        right values. This is intended for easier preparation of requests and
        results as well as limitations.

        :param quantity: The quantity, for which the template is requested,
            defaults to None
        :type quantity: Optional[str], optional
        :param method: The method, for which the template is requested, defaults
            to None
        :type method: Optional[str], optional
        :param currently_available: Indicator, whether only currently active
            capabilities shall be considered, defaults to True
        :type currently_available: bool, optional
        :return: A dictionary containing the quantity-method in the keys and the
            input and output schemas in a dictionary as the values
        :rtype: Dict[str, Dict[str, Any]]
        """

        schemas = self.get_capabilities(
            quantity=quantity, method=method, currently_available=currently_available
        )

        template_total = {}
        for schema in schemas:
            input_schema = schema.json_schema_specifications
            output_schema = schema.json_schema_result_output

            input_template = parse_schema_for_template(
                schema=input_schema,  # jsonref.replace_refs(input_schema),
                definitions={},
            )
            output_template = parse_schema_for_template(
                schema=output_schema,  # jsonref.replace_refs(output_schema),
                definitions={},
            )

            template_total[f"{schema.quantity}-{schema.method}"] = {
                "input_template": input_template,
                "output_template": output_template,
            }

        return template_total


def limitations_schema_translation(inputs_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates the limitations schema in a recursive way from parameters schema.
    """

    # Trivial case: if there are no parameters, there can be no limitations.
    if len(inputs_schema) == 0:
        return {"additionalProperties": False}

    limitations_schema: Dict[str, Any] = {}

    # The title is not necessary but may be useful for debugging at runtime
    if "title" in inputs_schema:
        limitations_schema["title"] = inputs_schema["title"]

    # For some reason, some of the schemas generated contain the "allOf"
    # keyword with a single list element instead of just that element.
    # If this is the case, just return the subschema of that.
    if "allOf" in inputs_schema:
        limitations_schema["allOf"] = []
        subschemas = inputs_schema["allOf"]
        if len(subschemas) > 1:
            raise ValueError(
                "Schema contains an instance of `allOf` with more than 1 element!"
            )
        subschema_translation = limitations_schema_translation(subschemas[0])
        limitations_schema["allOf"].append(subschema_translation)
        return limitations_schema

    # If the schema is actually one of many possible subschemas, there
    # might be different limitations for the different possible
    # sub-schemas.
    if "anyOf" in inputs_schema:
        limitations_schema["anyOf"] = []
        for subschema in inputs_schema["anyOf"]:
            subschema_translation = limitations_schema_translation(subschema)
            limitations_schema["anyOf"].append(subschema_translation)
        return limitations_schema

    # Every object in the schema can now be either an instance of what it
    # is already described (when that is the only option) or an array of
    # objects of that same type, with the possible values (or ranges).
    single_object_schema = {"type": inputs_schema["type"]}

    if inputs_schema["type"] == "array":
        # If the object was an array, the type is defined inside of "items".
        new_items = inputs_schema["items"]
        new_items = limitations_schema_translation(new_items)
        schema_items = new_items
        single_object_schema["items"] = new_items

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
        schema_items = {"anyOf": [range_schema, cases_schema]}

    else:
        # If the object was a string or any other type (except arrays
        # or numerics) the type is defined inside of "type" (duh). If
        # it was a string then this is over, but if it was another
        # custom type, I need to go throught its properties and add
        # them recursively.
        schema_items = {"type": inputs_schema["type"]}

        if "properties" in inputs_schema:
            subschema_properties = {}
            for propery_name, property_schema in inputs_schema["properties"].items():
                new_property = limitations_schema_translation(property_schema)
                subschema_properties[propery_name] = new_property
            schema_items["properties"] = subschema_properties
            single_object_schema["properties"] = subschema_properties

        if "additionalProperties" in inputs_schema:
            new_property = inputs_schema["additionalProperties"]
            new_property = limitations_schema_translation(new_property)
            schema_items["additionalProperties"] = new_property
            single_object_schema["additionalProperties"] = new_property

    # As stated before, the limitations can either be a single possible
    # instance of the schema, or the array.
    limitations_schema["anyOf"] = [
        single_object_schema,
        {"type": "array", "items": schema_items},
    ]

    return limitations_schema


def parse_schema_for_template(schema: dict, definitions: dict) -> Dict[str, Any]:
    """This function takes a json schema in and parses it to generate a template of the
    respective dictionary described in the schema.

    :param schema: The schema to parse. # TODO: The references need to be replaced!
    :type schema: dict
    :param template: The dictionary, which shall be used as the template
    :type template: dict
    :param definitions: The definitions section of a higher level part of the schema in
                        case the schema to parse is a part of a larger schema
    :type definitions: dict
    :return: A dictionary with the properties as keys and the generated templates as
             values
    :rtype: Dict[str, Any]
    """

    # Choose, how the types in the json schema shall be displayed in the template
    types_dict = {
        "number": "float",
        "integer": "int",
        "string": "str",
        "boolean": "bool",
    }

    template: dict = {}

    # Extract, the required fields and definitions from the schema
    required = schema.get("required", [])

    if "definitions" in schema.keys():
        definitions = schema["definitions"]
    elif "$defs" in schema.keys():
        definitions = schema["$defs"]

    if "type" not in schema.keys():
        return template
    if schema["type"] != "object":
        return template
    if "properties" not in schema.keys():
        return template

    for prop in schema["properties"].keys():
        requirement = "optional"
        if prop in required:
            requirement = "required"
        if "type" in schema["properties"][prop].keys():
            prop_type = schema["properties"][prop]["type"]
            if prop_type in types_dict.keys():
                template[prop] = f"{requirement}, {types_dict[prop_type]}"
            elif schema["properties"][prop]["type"] == "array":
                template[prop] = []
                iterator_type = type(schema["properties"][prop]["items"])
                if iterator_type == list:
                    iterator = schema["properties"][prop]["items"]
                elif iterator_type == dict:
                    iterator = [schema["properties"][prop]["items"]]
                for item in iterator:
                    if "type" in item.keys():
                        if item["type"] in types_dict.keys():
                            template[prop].append(
                                f"{requirement}, {types_dict[item['type']]}"
                            )
                        # TODO: The case of an item being a list is not yet
                        # covered.
                    if "$ref" in item.keys():
                        detail_key = item["$ref"].split("/")[-1]
                        template[prop].append(
                            parse_schema_for_template(
                                definitions[detail_key],
                                definitions=definitions,
                            )
                        )
            elif schema["properties"][prop]["type"] == "object":
                template[prop] = parse_schema_for_template(
                    schema["properties"][prop],
                    definitions=definitions,
                )
        elif "allOf" in schema["properties"][prop].keys():
            for allOf_type in schema["properties"][prop]["allOf"]:
                detail_key = allOf_type["$ref"].split("/")[-1]
                template[prop] = parse_schema_for_template(
                    definitions[detail_key],
                    definitions=definitions,
                )
        elif "anyOf" in schema["properties"][prop].keys():
            types = []
            for anyOf_item in schema["properties"][prop]["anyOf"]:
                for key in anyOf_item.keys():
                    anyOf_type = anyOf_item[key]
                    if "$ref" in key:
                        detail_key = anyOf_item["$ref"].split("/")[-1]
                        sub_template = parse_schema_for_template(
                            definitions[detail_key],
                            definitions=definitions,
                        )
                        types.append(str(sub_template))
                    elif "additionalProperties" in key:
                        detail_key = anyOf_item["additionalProperties"]["$ref"].split(
                            "/"
                        )[-1]
                        sub_template = {
                            f"{requirement}, "
                            "str": parse_schema_for_template(
                                definitions[detail_key],
                                definitions=definitions,
                            )
                        }
                        types.append(str(sub_template))
                    elif "type" == key:
                        if anyOf_type in types_dict.keys():
                            types.append(types_dict[anyOf_type])
                        elif anyOf_type == "array":
                            typelist = []
                            for prefix_item in anyOf_item["prefixItems"]:
                                typelist.append(types_dict[prefix_item["type"]])
                            if ("maxItems" in anyOf_item.keys()) and (
                                "minItems" in anyOf_item.keys()
                            ):
                                if anyOf_item["maxItems"] == anyOf_item["minItems"]:
                                    typestuple = tuple(typelist)
                                    types.append(str(typestuple))
                                else:
                                    types.append(str(typelist))
                        elif anyOf_type == "null":
                            requirement_subprop = "optional"
            template[prop] = f"{requirement_subprop}, {' or '.join(types)}"

    return template
