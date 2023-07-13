from FINALES2.schemas import GeneralMetaData, Quantity, ServerConfig
from FINALES2.tenants.referenceTenant import Tenant
from FINALES2.user_management.classes_user_manager import User

GeneralMetaData_obj = GeneralMetaData(
    name="EOF_tenant",
    description="End of life prediction ML model",
)

quantities = {
    "degradationEOL": Quantity(
        name="degradationEOL",
        methods={
            "name": "degradation_model",
            "quantity": "degradationEOL",
            "parameters": [
                "chemistry",
                "input_cycles",
                "average_charging_rate",
                "maximum_charging_rate",
                "minimum_charging_rate",
                "delta_coulombic_efficiency",
                "voltage_gap_charge_discharge",
                "capacity_vector_variance",
            ],
            "limitations": {
                "chemistry": {
                    "electrolyte": [
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
                    ],
                    "anode": {
                        "material": [
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
                        ],
                        "mass_loading": [
                            {
                                "min": 1.12,  # Unknown quantity, guess
                                "max": 1.2,
                            }
                        ],
                        # "size": [
                        #     {
                        #         "min": 1.12, # Unknown quantity, guess
                        #         "max": 1.2,
                        #     }
                        # ],
                        # "material_info": {
                        #     "name": "optional, str",
                        #     "uuid": "optional, str",
                        #     "preparation_date": "optional, str",
                        #     "batch": "optional, str"
                        # }
                    },
                    "cathode": {
                        "material": [
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
                        ],
                        "mass_loading": [
                            {
                                "min": 1.02,  # Unknown quantity, guess
                                "max": 1.3,
                            }
                        ],
                        # "size": [ # This is optional
                        #     {
                        #         "min": 4, # Unknown quantity, guess
                        #         "max": 5,  # Area
                        #     }
                        # ],
                        # "material_info": {
                        #     "name": "optional, str",
                        #     "uuid": "optional, str",
                        #     "preparation_date": "optional, str",
                        #     "batch": "optional, str"
                        # }
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
    run_method="temp",  # Lauras run function,
    prepare_results="temp",  # Lauras function,
    FINALES_server_config=ServerConfig(host="", port=""),
    # end_run_time # not neccesary
    # authorization_header= # optional # This is done automatically when it is logged in
    operator=User(username="Simon", password="Simon1", usergroups=["BIG-MAP"]),
    tenant_user=User(
        username="degradationEOL", password="degradationEOL1", usergroups=["BIG-MAP"]
    ),
    tenant_uuid="temp",
)


# Generate json for tenant registration
...
# Recieve uuid
# EOF_tenant.tenant_uuid = admin_recieved_uuid


# Calling the function
EOF_tenant.run()
