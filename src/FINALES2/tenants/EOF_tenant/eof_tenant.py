import json
from datetime import datetime

from FINALES2.schemas import GeneralMetaData, Method, Quantity, ServerConfig
from FINALES2.tenants.referenceTenant import Tenant
from FINALES2.user_management.classes_user_manager import User

# from .eol_degradation.src.eolDegradationMethod import prepare_my_result, run_my_method


def run_my_method():
    pass


def prepare_my_result():
    pass


GeneralMetaData_obj = GeneralMetaData(
    name="EOF_tenant",
    description="End of life prediction ML model",
)
quantities = {
    "degradationEOL": Quantity(
        name="degradationEOL",
        methods={
            "degradation_model": Method(
                name="degradation_model",
                quantity="degradationEOL",
                parameters=[
                    "chemistry",
                    "input_cycles",
                    "average_charging_rate",
                    "maximum_charging_rate",
                    "minimum_charging_rate",
                    "delta_coulombic_efficiency",
                    "voltage_gap_charge_discharge",
                    "capacity_vector_variance",
                ],
                limitations={
                    "chemistry": {
                        "electrolyte": [
                            [
                                {
                                    "chemical": {
                                        "SMILES": ["SMILES str"],
                                        "InChIKey": ["InchiKey str"],
                                    },
                                    "fraction": [
                                        {
                                            "min": 0.0,
                                            "max": 1.0,
                                        }
                                    ],
                                    "fraction_type": ["molPerMol"],
                                }
                            ]
                        ],
                        "anode": {
                            "material": [
                                [
                                    {
                                        "chemical": {
                                            "SMILES": ["Anode SMILES"],
                                            "InChIKey": ["Anode InchiKey"],
                                        },
                                        "fraction": [
                                            {
                                                "min": 0.2,
                                                "max": 1.0,
                                            },
                                            0,
                                        ],
                                        "fraction_type": ["molPerMol"],
                                    }
                                ]
                            ],
                            "mass_loading": [
                                {
                                    "min": 1.12,  # Unknown quantity, guess
                                    "max": 1.2,
                                }
                            ],
                        },
                        "cathode": {
                            "material": [
                                [
                                    {
                                        "chemical": {
                                            "SMILES": ["Cathode SMILES"],
                                            "InChIKey": ["Cathode InchiKey"],
                                        },
                                        "fraction": [
                                            {
                                                "min": 0.2,
                                                "max": 0.8,
                                            },
                                            0,
                                        ],
                                        "fraction_type": ["molPerMol"],
                                    }
                                ]
                            ],
                            "mass_loading": [
                                {
                                    "min": 1.02,  # Unknown quantity, guess
                                    "max": 1.3,
                                }
                            ],
                        },
                    },
                    "input_cycles": [{"min": 1, "max": 200, "step": 1}],
                    "average_charging_rate": [
                        {
                            "min": 0.0,
                            "max": 1.0,  # somewhat a guess
                        }
                    ],
                    "maximum_charging_rate": [
                        {
                            "min": 0.0,
                            "max": 1.0,  # somewhat a guess
                        }
                    ],
                    "minimum_charging_rate": [
                        {
                            "min": 0.0,
                            "max": 1.0,  # somewhat a guess
                        }
                    ],
                    "delta_coulombic_efficiency": [
                        {
                            "min": 0.0,
                            "max": 1.0,  # somewhat a guess
                        }
                    ],
                    "voltage_gap_charge_discharge": [
                        {
                            "min": 0.0,
                            "max": 1.0,  # somewhat a guess
                        }
                    ],
                    "capacity_vector_variance": [
                        {
                            "min": 0.0,
                            "max": 1.0,  # somewhat a guess
                        }
                    ],
                },
            )
        },
        is_active=True,
    )
}
EOF_tenant = Tenant(
    general_meta=GeneralMetaData_obj,
    quantities=quantities,
    # queue: list = [] # Not necessary
    sleep_time_s=7200,  # two hours
    tenant_config="Monika & Simon Deployment",
    run_method=run_my_method,  # Lauras run function,
    prepare_results=prepare_my_result,  # Lauras function,
    FINALES_server_config=ServerConfig(
        host="0.0.0.0", port=8888
    ),  # host=134.60.56.11, port=44188
    end_run_time=datetime(
        year=2024, month=7, day=26
    ),  # not neccesary; TODO: Adapt to new type!
    authorization_header={},  # optional # This is done automatically when it is logged
    # in
    operator=User(username="Simon", password="Simon1", usergroups=["BIG-MAP"]),
    # operators=[User(username="Simon", password="Simon1", usergroups=["BIG-MAP"])],
    tenant_user=User(
        username="degradationEOL", password="degradationEOL1", usergroups=["BIG-MAP"]
    ),
    tenant_uuid="my_tenant_UUID",
)

example_input = {
    "chemistry": {
        "electrolyte": [
            {
                "chemical": {
                    "SMILES": "CCOC(=O)OC",
                    "InChIKey": "JBTWLSYIZRCDFO-UHFFFAOYSA-N",
                },
                "fraction": 1.0,
                "fraction_type": "molPerMol",
            }
        ],
        "anode": {
            "material": [
                {
                    "chemical": {
                        "SMILES": "[C]",
                        "InChIKey": "OKTJSMMVPCPJKN-UHFFFAOYSA-N",
                    },
                    "fraction": 1.0,
                    "fraction_type": "molPerMol",
                }
            ],
            "mass_loading": 1.1,
            "size": 15.0,
        },
        "cathode": {
            "material": [
                {
                    "chemical": {
                        "SMILES": "[Li+].[O-][Co]=O",
                        "InChIKey": "BFZPBUKRYWOWDV-UHFFFAOYSA-N",
                    },
                    "fraction": 1.0,
                    "fraction_type": "molPerMol",
                }
            ],
            "mass_loading": 1.1,
            "size": 14.0,
        },
    },
    "input_cycles": 40,
    "average_charging_rate": 0.1,
    "maximum_charging_rate": 0.15,
    "minimum_charging_rate": 0.7,
    "delta_coulombic_efficiency": 0.2,
    "voltage_gap_charge_discharge": 0.4,
    "capacity_vector_variance": 0.03,
}

example_output = {
    "run_info": {
        "formulation": [
            {
                "chemical": {
                    "SMILES": "CCOC(=O)OC",
                    "InChIKey": "JBTWLSYIZRCDFO-UHFFFAOYSA-N",
                },
                "fraction": 1.0,
                "fraction_type": "molPerMol",
            }
        ],
        "internal_reference": "An ID assigned by the tenant",
        # TODO: add the functionality to assign an internal ID
        "formulation_info": {
            "name": "EMC",
            "uuid": "1234",
            "preparation_date": "26.07.2023",
            "batch": "26-07-2023_01_A",
            "location": {
                "address": "example street 1",
                "detail_1": "building A",
                "detail_2": "cluster B",
            },
        },
        "chemicals_info": {
            "JBTWLSYIZRCDFO-UHFFFAOYSA-N": {
                "name": "EMC",
                "molar_mass": (104.1, 0.001),
                "density": (1.07, 0.005),
                "batch": "manufacturer_batch_1",
                "manufacturer": "example_manufacturer_1",
                "manufacturing_date": "26.07.2023",
            },
            "OKTJSMMVPCPJKN-UHFFFAOYSA-N": {
                "name": "Graphite",
                "molar_mass": (12.011, 0.001),
                "density": (2.2, 0.005),
                "batch": "manufacturer_batch_234",
                "manufacturer": "example_manufacturer_2",
                "manufacturing_date": "26.07.2023",
            },
            "BFZPBUKRYWOWDV-UHFFFAOYSA-N": {
                "name": "Lithium cobaltoxide",
                "molar_mass": (97.9, 0.001),
                "density": (3.5, 0.005),
                "batch": "manufacturer_batch_r839",
                "manufacturer": "example_manufacturer_3",
                "manufacturing_date": "26.07.2023",
            },
        },
    },
    "degradationEOL": {
        "end_of_life": 400,
        "end_of_life_uncertainty": 5.9,
        "capacity_trajectory": [3.2, 2.9, 2.6, 2.4, 2.0],
        "capacity_trajectory_uncertainty": [0.04, 0.009, 0.02, 0.0005, 0.01],
        "meta": {"success": True, "rating": 5},
    },
}


def tenant_object_to_json(tenant):
    """
    Funciton for creating the json input file, which is to be forwarded to the admin
    for registering a tenant.

    The uuid will be returned by the admin, which the user then will add to there
    Tenant object tenant_uuid field.
    """

    limitations = []
    capability_keys = list(tenant.quantities.keys())
    for capa_key in capability_keys:
        method_keys = list(tenant.quantities[capa_key].methods.keys())
        for method_key in method_keys:
            limitations.append(
                {
                    "quantity": capa_key,
                    "method": method_key,
                    "limitations": tenant.quantities[capa_key]
                    .methods[method_key]
                    .limitations,
                }
            )

    output_dict = {
        "name": tenant.general_meta.name,
        "limitations": limitations,
        "contact_person": str(tenant.operator.username),
    }

    with open(f"{tenant.general_meta.name}_tenant.json", "w") as fp:
        json.dump(output_dict, fp, indent=2)

    return


# Generate json for tenant registration
# Recieve uuid
# EOF_tenant.tenant_uuid = admin_recieved_uuid
tenant_object_to_json(EOF_tenant)
# EOF_tenant.tenant_object_to_json()
# Calling the function
# EOF_tenant.run()
