from FINALES2.engine.server_manager import parse_schema_for_template


# Test to fix of the issue, that a "$ref" key is not found, if a list of lists is in an
# anyOf key
def test_list_of_lists():
    schema_list_of_lists = {
        "$defs": {
            "Chemical": {
                "description": "Subclass",
                "properties": {
                    "SMILES": {
                        "description": "A SMILES string representing the chemical.",
                        "title": "Smiles",
                        "type": "string",
                    },
                    "InChIKey": {
                        "description": (
                            "The hashed standard International Chemical "
                            "Identifier of the chemical to ensure "
                            "machine-readability."
                        ),
                        "title": "Inchikey",
                        "type": "string",
                    },
                },
                "required": ["SMILES", "InChIKey"],
                "title": "Chemical",
                "type": "object",
            },
            "ChemicalInfo": {
                "description": (
                    "Additional information about a chemical, which is "
                    "relevant for documentation\n    purposes"
                ),
                "properties": {
                    "name": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "description": (
                            "A human readable name of the chemical, "
                            "to which this information is referring."
                        ),
                        "title": "Name",
                    },
                    "molar_mass": {
                        "anyOf": [
                            {
                                "maxItems": 2,
                                "minItems": 2,
                                "prefixItems": [{"type": "number"}, {"type": "number"}],
                                "type": "array",
                            },
                            {"type": "null"},
                        ],
                        "description": (
                            "The molar mass of the chemical and the "
                            "correcponding uncertainty. This may be a "
                            "measured quantity or a literature value. "
                            "It is needed to convert between volumetric "
                            "and molar ratios and this field serves to "
                            "report the used value. Unit: gram / mole"
                        ),
                        "title": "Molar Mass",
                        "unit": "gram / mole",
                    },
                    "density": {
                        "anyOf": [
                            {
                                "maxItems": 2,
                                "minItems": 2,
                                "prefixItems": [{"type": "number"}, {"type": "number"}],
                                "type": "array",
                            },
                            {"type": "null"},
                        ],
                        "description": (
                            "The density of the chemical and the "
                            "correcponding uncertainty. This may be a "
                            "measured quantity or a literature value. "
                            "It is needed to convert between volumetric "
                            "and molar ratios and this field serves to "
                            "report the used value. "
                            "Unit: centimeter ** 3 * gram"
                        ),
                        "title": "Density",
                        "unit": "centimeter ** 3 * gram",
                    },
                    "batch": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "description": (
                            "A batch number for the chemical used, "
                            "if it is available."
                        ),
                        "title": "Batch",
                    },
                    "manufacturer": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "description": (
                            "The manufacturer of the chemical, " "if it is available."
                        ),
                        "title": "Manufacturer",
                    },
                    "manufacturing_date": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "description": "The date when the chemical was manufactured.",
                        "title": "Manufacturing Date",
                    },
                },
                "required": [
                    "name",
                    "molar_mass",
                    "density",
                    "batch",
                    "manufacturer",
                    "manufacturing_date",
                ],
                "title": "ChemicalInfo",
                "type": "object",
            },
            "ConductivityOutput": {
                "description": (
                    "\n    Results returned from the following quantities:"
                    "\n    'conductivity' - 'two_electrode'\n    "
                    "'conductivity' - 'molecular_dynamics_conductivity'"
                    "\n    "
                ),
                "properties": {
                    "values": {
                        "description": (
                            "The values determined for the conductivity. "
                            "Unit: siemens / meter"
                        ),
                        "items": {"type": "number"},
                        "title": "Values",
                        "type": "array",
                        "unit": "siemens / meter",
                    },
                    "temperature": {
                        "anyOf": [{"type": "number"}, {"type": "null"}],
                        "description": (
                            "This is the actual temperature of the "
                            "measuring cell or used in a simulation. "
                            "Unit: kelvin"
                        ),
                        "title": "Temperature",
                        "unit": "kelvin",
                    },
                    "meta": {
                        "allOf": [{"$ref": "#/$defs/MethodMeta"}],
                        "description": (
                            "This field provides information regarding "
                            "the reliability of the reported data. "
                            "E.g. the success of the method for this "
                            "quantity and the rating of the data. This is "
                            "for this specific quantity, because a single "
                            "method could fail individually for different "
                            "quantities. It is not included in the "
                            "RunInfo as one run may generate data for "
                            "different quantities, for which the methods "
                            "may fail individually."
                        ),
                    },
                },
                "required": ["values", "temperature", "meta"],
                "title": "ConductivityOutput",
                "type": "object",
            },
            "DensityOutput": {
                "description": (
                    "\n    Results returned from the following quantities:"
                    "\n    `density` - `vibrating_tube_densimetry`\n    "
                    "`density` - `molecular_dynamics_density`\n    "
                ),
                "properties": {
                    "values": {
                        "description": (
                            "The values determined for the density. "
                            "Unit: gram / centimeter ** 3"
                        ),
                        "items": {"type": "number"},
                        "title": "Values",
                        "type": "array",
                        "unit": "gram / centimeter ** 3",
                    },
                    "temperature": {
                        "anyOf": [{"type": "number"}, {"type": "null"}],
                        "description": (
                            "This is the actual temperature of measuring "
                            "cell. Unit: kelvin"
                        ),
                        "title": "Temperature",
                        "unit": "kelvin",
                    },
                    "meta": {
                        "allOf": [{"$ref": "#/$defs/MethodMeta"}],
                        "description": (
                            "This field provides information regarding "
                            "the reliability of the reported data. "
                            "E.g. the success of the method for this "
                            "quantity and the rating of the data. This "
                            "is for this specific quantity, because a "
                            "single method could fail individually for "
                            "different quantities. It is not included in "
                            "the RunInfo as one run may generate data for "
                            "different quantities, for which the methods "
                            "may fail individually."
                        ),
                    },
                },
                "required": ["values", "temperature", "meta"],
                "title": "DensityOutput",
                "type": "object",
            },
            "FormulationComponent": {
                "description": (
                    "This class shall be used when referring to chemicals "
                    "as a component in a formulation.\n    When "
                    "assembling a formulation based on "
                    "FormulationComponents, consider, that it\n    "
                    "might be required to use the same fraction type "
                    "for all the chemicals.\n    "
                ),
                "properties": {
                    "chemical": {
                        "allOf": [{"$ref": "#/$defs/Chemical"}],
                        "description": (
                            "The chemical, which shall be described as "
                            "a component in a solution ."
                        ),
                    },
                    "fraction": {
                        "description": (
                            "The unitless fraction of the chemical "
                            "in the total of the mixture."
                        ),
                        "title": "Fraction",
                        "type": "number",
                    },
                    "fraction_type": {
                        "description": (
                            "A string defining, what kind of a fraction "
                            "is given in the formulation. This can be "
                            "for example molar fractions, volume "
                            "fractions, mass fractions,.... At the moment "
                            "only molar fractions are supported."
                        ),
                        "title": "Fraction Type",
                        "type": "string",
                    },
                },
                "required": ["chemical", "fraction", "fraction_type"],
                "title": "FormulationComponent",
                "type": "object",
            },
            "FormulationInfo": {
                "description": (
                    "Additional information about a formulation, "
                    "which is relevant for documentation\n    purposes"
                ),
                "properties": {
                    "name": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "description": "A human readable name of the formulation.",
                        "title": "Name",
                    },
                    "uuid": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "description": (
                            "A unique identifier assigned to this "
                            "formulation in this run."
                        ),
                        "title": "Uuid",
                    },
                    "preparation_date": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "description": (
                            "The date when the formulation was prepared. "
                            "For commercial formulations, the "
                            "manufacturing date may be used."
                        ),
                        "title": "Preparation Date",
                    },
                    "batch": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "description": (
                            "A batch number for the formulation, " "if it is available."
                        ),
                        "title": "Batch",
                    },
                    "location": {
                        "anyOf": [{"$ref": "#/$defs/Location"}, {"type": "null"}],
                        "description": (
                            "The location, where the physical formulation "
                            "can be found, which corresponds to this "
                            "specification."
                        ),
                    },
                },
                "required": ["name", "uuid", "preparation_date", "batch", "location"],
                "title": "FormulationInfo",
                "type": "object",
            },
            "Location": {
                "description": (
                    " The location providing information on where to "
                    "find physical samples or\n    equipment."
                ),
                "properties": {
                    "address": {
                        "description": (
                            "The physical address, where the object can "
                            "be found. Depending on the usecase, this "
                            "may be an official address or a name of an "
                            "instute or similar. The default should be "
                            "an address."
                        ),
                        "title": "Address",
                        "type": "string",
                    },
                    "detail_1": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "description": (
                            "A more detailed description of a location. "
                            "This may be e.g. a specific laboratory in "
                            "a building, a desk in an office or a device "
                            "or a cabinet."
                        ),
                        "title": "Detail 1",
                    },
                    "detail_2": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "description": (
                            "Another level of detail for a location. "
                            "This may be e.g. a bench in the laboratory, "
                            "a shelf in a cabinet  or a specific port in "
                            "a machine."
                        ),
                        "title": "Detail 2",
                    },
                },
                "required": ["address", "detail_1", "detail_2"],
                "title": "Location",
                "type": "object",
            },
            "MethodMeta": {
                "description": (
                    "Additional information obtained from a method "
                    "summarizing information, whether \n    the method "
                    "was successfully run and what the rating for the "
                    "returned data is.\n    "
                ),
                "properties": {
                    "success": {
                        "description": (
                            "This reports, if the method finished " "successfully."
                        ),
                        "title": "Success",
                        "type": "boolean",
                    },
                    "rating": {
                        "description": (
                            "This field serves to rate the quality of the "
                            "result from the tenant side. It shall serve "
                            "as a support for the recieving party upon "
                            "evaluating the trustworthiness of the result. "
                            "It shall range from 0 (lowest) to 5 "
                            "(highest)."
                        ),
                        "title": "Rating",
                        "type": "integer",
                    },
                },
                "required": ["success", "rating"],
                "title": "MethodMeta",
                "type": "object",
            },
            "RDFOutput": {
                "description": (
                    "\n    Results returned from the following quantities:"
                    "\n    'radial_density_function' - "
                    "'molecular_dynamics_RDF'\n    "
                ),
                "properties": {
                    "radius": {
                        "description": (
                            "The radius at which atoms of the respecive "
                            "species appear."
                        ),
                        "items": {"type": "number"},
                        "title": "Radius",
                        "type": "array",
                        "unit": "angstrom",
                    },
                    "pair_title": {
                        "description": "The names of the pairs of atoms considered.",
                        "items": {"type": "string"},
                        "title": "Pair Title",
                        "type": "array",
                    },
                    "RDF": {
                        "description": (
                            "Quotient between the local particle density "
                            "at radius r and the average density of the "
                            "system."
                        ),
                        "items": {"items": {"type": "number"}, "type": "array"},
                        "title": "Rdf",
                        "type": "array",
                    },
                    "cell_volume": {
                        "description": (
                            "The volume of the cell under concideration. "
                            "Unit: angstrom ** 3"
                        ),
                        "title": "Cell Volume",
                        "type": "number",
                        "unit": "angstrom ** 3",
                    },
                    "cell_formula": {
                        "description": (
                            "The composition of the considered cell "
                            "reporting the number of atoms per type "
                            "contained in the cell, "
                            "e.g. Li16 O600 P16 F96 C600 H600"
                        ),
                        "title": "Cell Formula",
                        "type": "string",
                    },
                },
                "required": [
                    "radius",
                    "pair_title",
                    "RDF",
                    "cell_volume",
                    "cell_formula",
                ],
                "title": "RDFOutput",
                "type": "object",
            },
            "RunInfo": {
                "description": (
                    "Metadata for a run of a method. This information may "
                    "apply to all samples\n    processed in the respective "
                    "run.\n    "
                ),
                "properties": {
                    "formulation": {
                        "description": (
                            "This is a formulation defining the Chemicals "
                            "contained in thesample and their fraction "
                            "in the total mixture."
                        ),
                        "items": {"$ref": "#/$defs/FormulationComponent"},
                        "title": "Formulation",
                        "type": "array",
                    },
                    "internal_reference": {
                        "description": (
                            "This field is an internal ID identifying "
                            "this run of the method. In experimental "
                            "setups, this may reference to an ID of "
                            "the sample."
                        ),
                        "title": "Internal Reference",
                        "type": "string",
                    },
                    "formulation_info": {
                        "anyOf": [
                            {"$ref": "#/$defs/FormulationInfo"},
                            {"type": "null"},
                        ],
                        "description": (
                            "This is the metadata concerning the "
                            "formulation relevant for documentation."
                        ),
                    },
                    "chemicals_info": {
                        "anyOf": [
                            {
                                "additionalProperties": {
                                    "$ref": "#/$defs/ChemicalInfo"
                                },
                                "type": "object",
                            },
                            {"type": "null"},
                        ],
                        "description": (
                            "This is a dictionary of metadata of the "
                            "chemicals relevant for documentation. The "
                            "keys are InChIKeys of the chemicals "
                            "contained in the formulation and the values "
                            "are ChemicalInfo objects."
                        ),
                        "title": "Chemicals Info",
                    },
                },
                "required": [
                    "formulation",
                    "internal_reference",
                    "formulation_info",
                    "chemicals_info",
                ],
                "title": "RunInfo",
                "type": "object",
            },
        },
        "description": (
            "\n    Results returned from the following quantities:\n    "
            "'conductivity' - 'molecular_dynamics_conductivity'\n    "
        ),
        "properties": {
            "run_info": {
                "allOf": [{"$ref": "#/$defs/RunInfo"}],
                "description": (
                    "The information regarding the formulation and the "
                    "internal reference, which is common for all data "
                    "generated in this run of the method."
                ),
            },
            "conductivity": {
                "allOf": [{"$ref": "#/$defs/ConductivityOutput"}],
                "description": "The output generated for the conductivity data.",
            },
            "density": {
                "anyOf": [{"$ref": "#/$defs/DensityOutput"}, {"type": "null"}],
                "description": (
                    "The ouptut of density calculations, "
                    "which were generated as a side result."
                ),
            },
            "RDF": {
                "anyOf": [{"$ref": "#/$defs/RDFOutput"}, {"type": "null"}],
                "description": (
                    "The ouptut of RDF calculations, which were "
                    "generated as a side result."
                ),
            },
            "number_molecules_per_component": {
                "anyOf": [
                    {"additionalProperties": {"type": "integer"}, "type": "object"},
                    {"type": "null"},
                ],
                "description": (
                    "The absolute number of molecules for each chemical "
                    "contained in the formulation."
                ),
                "title": "Number Molecules Per Component",
            },
        },
        "required": [
            "run_info",
            "conductivity",
            "density",
            "RDF",
            "number_molecules_per_component",
        ],
        "title": "MolecularDynamicsOutput",
        "type": "object",
    }

    definitions_list_of_lists = {
        "Chemical": {
            "description": "Subclass",
            "properties": {
                "SMILES": {
                    "description": "A SMILES string representing the chemical.",
                    "title": "Smiles",
                    "type": "string",
                },
                "InChIKey": {
                    "description": (
                        "The hashed standard International Chemical "
                        "Identifier of the chemical to ensure "
                        "machine-readability."
                    ),
                    "title": "Inchikey",
                    "type": "string",
                },
            },
            "required": ["SMILES", "InChIKey"],
            "title": "Chemical",
            "type": "object",
        },
        "ChemicalInfo": {
            "description": (
                "Additional information about a chemical, which is "
                "relevant for documentation\n    purposes"
            ),
            "properties": {
                "name": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "description": (
                        "A human readable name of the chemical, to which "
                        "this information is referring."
                    ),
                    "title": "Name",
                },
                "molar_mass": {
                    "anyOf": [
                        {
                            "maxItems": 2,
                            "minItems": 2,
                            "prefixItems": [{"type": "number"}, {"type": "number"}],
                            "type": "array",
                        },
                        {"type": "null"},
                    ],
                    "description": (
                        "The molar mass of the chemical and the "
                        "correcponding uncertainty. This may be a "
                        "measured quantity or a literature value. It is "
                        "needed to convert between volumetric and molar "
                        "ratios and this field serves to report the "
                        "used value. Unit: gram / mole"
                    ),
                    "title": "Molar Mass",
                    "unit": "gram / mole",
                },
                "density": {
                    "anyOf": [
                        {
                            "maxItems": 2,
                            "minItems": 2,
                            "prefixItems": [{"type": "number"}, {"type": "number"}],
                            "type": "array",
                        },
                        {"type": "null"},
                    ],
                    "description": (
                        "The density of the chemical and the "
                        "correcponding uncertainty. This may be a "
                        "measured quantity or a literature value. It is "
                        "needed to convert between volumetric and molar "
                        "ratios and this field serves to report the used "
                        "value. Unit: centimeter ** 3 * gram"
                    ),
                    "title": "Density",
                    "unit": "centimeter ** 3 * gram",
                },
                "batch": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "description": (
                        "A batch number for the chemical used, " "if it is available."
                    ),
                    "title": "Batch",
                },
                "manufacturer": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "description": (
                        "The manufacturer of the chemical, " "if it is available."
                    ),
                    "title": "Manufacturer",
                },
                "manufacturing_date": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "description": "The date when the chemical was manufactured.",
                    "title": "Manufacturing Date",
                },
            },
            "required": [
                "name",
                "molar_mass",
                "density",
                "batch",
                "manufacturer",
                "manufacturing_date",
            ],
            "title": "ChemicalInfo",
            "type": "object",
        },
        "ConductivityOutput": {
            "description": (
                "\n    Results returned from the following quantities:"
                "\n    'conductivity' - 'two_electrode'\n    "
                "'conductivity' - 'molecular_dynamics_conductivity'\n    "
            ),
            "properties": {
                "values": {
                    "description": (
                        "The values determined for the conductivity. "
                        "Unit: siemens / meter"
                    ),
                    "items": {"type": "number"},
                    "title": "Values",
                    "type": "array",
                    "unit": "siemens / meter",
                },
                "temperature": {
                    "anyOf": [{"type": "number"}, {"type": "null"}],
                    "description": (
                        "This is the actual temperature of the measuring "
                        "cell or used in a simulation. Unit: kelvin"
                    ),
                    "title": "Temperature",
                    "unit": "kelvin",
                },
                "meta": {
                    "allOf": [{"$ref": "#/$defs/MethodMeta"}],
                    "description": (
                        "This field provides information regarding the "
                        "reliability of the reported data. E.g. the "
                        "success of the method for this quantity and the "
                        "rating of the data. This is for this specific "
                        "quantity, because a single method could fail "
                        "individually for different quantities. It is "
                        "not included in the RunInfo as one run may "
                        "generate data for different quantities, for "
                        "which the methods may fail individually."
                    ),
                },
            },
            "required": ["values", "temperature", "meta"],
            "title": "ConductivityOutput",
            "type": "object",
        },
        "DensityOutput": {
            "description": (
                "\n    Results returned from the following quantities:"
                "\n    `density` - `vibrating_tube_densimetry`\n    "
                "`density` - `molecular_dynamics_density`\n    "
            ),
            "properties": {
                "values": {
                    "description": (
                        "The values determined for the density. "
                        "Unit: gram / centimeter ** 3"
                    ),
                    "items": {"type": "number"},
                    "title": "Values",
                    "type": "array",
                    "unit": "gram / centimeter ** 3",
                },
                "temperature": {
                    "anyOf": [{"type": "number"}, {"type": "null"}],
                    "description": (
                        "This is the actual temperature of measuring "
                        "cell. Unit: kelvin"
                    ),
                    "title": "Temperature",
                    "unit": "kelvin",
                },
                "meta": {
                    "allOf": [{"$ref": "#/$defs/MethodMeta"}],
                    "description": (
                        "This field provides information regarding the "
                        "reliability of the reported data. E.g. the "
                        "success of the method for this quantity and the "
                        "rating of the data. This is for this specific "
                        "quantity, because a single method could fail "
                        "individually for different quantities. It is "
                        "not included in the RunInfo as one run may "
                        "generate data for different quantities, for "
                        "which the methods may fail individually."
                    ),
                },
            },
            "required": ["values", "temperature", "meta"],
            "title": "DensityOutput",
            "type": "object",
        },
        "FormulationComponent": {
            "description": (
                "This class shall be used when referring to chemicals as "
                "a component in a formulation.\n    When assembling a "
                "formulation based on FormulationComponents, consider, "
                "that it\n    might be required to use the same fraction "
                "type for all the chemicals.\n    "
            ),
            "properties": {
                "chemical": {
                    "allOf": [{"$ref": "#/$defs/Chemical"}],
                    "description": (
                        "The chemical, which shall be described as a "
                        "component in a solution ."
                    ),
                },
                "fraction": {
                    "description": (
                        "The unitless fraction of the chemical "
                        "in the total of the mixture."
                    ),
                    "title": "Fraction",
                    "type": "number",
                },
                "fraction_type": {
                    "description": (
                        "A string defining, what kind of a fraction is "
                        "given in the formulation. This can be for example "
                        "molar fractions, volume fractions, mass "
                        "fractions,.... At the moment only molar "
                        "fractions are supported."
                    ),
                    "title": "Fraction Type",
                    "type": "string",
                },
            },
            "required": ["chemical", "fraction", "fraction_type"],
            "title": "FormulationComponent",
            "type": "object",
        },
        "FormulationInfo": {
            "description": (
                "Additional information about a formulation, which is "
                "relevant for documentation\n    purposes"
            ),
            "properties": {
                "name": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "description": "A human readable name of the formulation.",
                    "title": "Name",
                },
                "uuid": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "description": (
                        "A unique identifier assigned to this "
                        "formulation in this run."
                    ),
                    "title": "Uuid",
                },
                "preparation_date": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "description": (
                        "The date when the formulation was prepared. "
                        "For commercial formulations, the manufacturing "
                        "date may be used."
                    ),
                    "title": "Preparation Date",
                },
                "batch": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "description": (
                        "A batch number for the formulation, " "if it is available."
                    ),
                    "title": "Batch",
                },
                "location": {
                    "anyOf": [{"$ref": "#/$defs/Location"}, {"type": "null"}],
                    "description": (
                        "The location, where the physical formulation can "
                        "be found, which corresponds to this "
                        "specification."
                    ),
                },
            },
            "required": ["name", "uuid", "preparation_date", "batch", "location"],
            "title": "FormulationInfo",
            "type": "object",
        },
        "Location": {
            "description": (
                " The location providing information on where to "
                "find physical samples or\n    equipment."
            ),
            "properties": {
                "address": {
                    "description": (
                        "The physical address, where the object can be "
                        "found. Depending on the usecase, this may be an "
                        "official address or a name of an instute or "
                        "similar. The default should be an address."
                    ),
                    "title": "Address",
                    "type": "string",
                },
                "detail_1": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "description": (
                        "A more detailed description of a location. "
                        "This may be e.g. a specific laboratory in a "
                        "building, a desk in an office or a device or "
                        "a cabinet."
                    ),
                    "title": "Detail 1",
                },
                "detail_2": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "description": (
                        "Another level of detail for a location. This "
                        "may be e.g. a bench in the laboratory, a shelf "
                        "in a cabinet  or a specific port in a machine."
                    ),
                    "title": "Detail 2",
                },
            },
            "required": ["address", "detail_1", "detail_2"],
            "title": "Location",
            "type": "object",
        },
        "MethodMeta": {
            "description": (
                "Additional information obtained from a method "
                "summarizing information, whether \n    the method was "
                "successfully run and what the rating for the returned "
                "data is.\n    "
            ),
            "properties": {
                "success": {
                    "description": "This reports, if the method finished successfully.",
                    "title": "Success",
                    "type": "boolean",
                },
                "rating": {
                    "description": (
                        "This field serves to rate the quality of the "
                        "result from the tenant side. It shall serve as "
                        "a support for the recieving party upon "
                        "evaluating the trustworthiness of the result. "
                        "It shall range from 0 (lowest) to 5 (highest)."
                    ),
                    "title": "Rating",
                    "type": "integer",
                },
            },
            "required": ["success", "rating"],
            "title": "MethodMeta",
            "type": "object",
        },
        "RDFOutput": {
            "description": (
                "\n    Results returned from the following quantities:\n"
                "    'radial_density_function' - "
                "'molecular_dynamics_RDF'\n    "
            ),
            "properties": {
                "radius": {
                    "description": (
                        "The radius at which atoms of the respecive " "species appear."
                    ),
                    "items": {"type": "number"},
                    "title": "Radius",
                    "type": "array",
                    "unit": "angstrom",
                },
                "pair_title": {
                    "description": "The names of the pairs of atoms considered.",
                    "items": {"type": "string"},
                    "title": "Pair Title",
                    "type": "array",
                },
                "RDF": {
                    "description": (
                        "Quotient between the local particle density at "
                        "radius r and the average density of the system."
                    ),
                    "items": {"items": {"type": "number"}, "type": "array"},
                    "title": "Rdf",
                    "type": "array",
                },
                "cell_volume": {
                    "description": (
                        "The volume of the cell under concideration. "
                        "Unit: angstrom ** 3"
                    ),
                    "title": "Cell Volume",
                    "type": "number",
                    "unit": "angstrom ** 3",
                },
                "cell_formula": {
                    "description": (
                        "The composition of the considered cell reporting "
                        "the number of atoms per type contained in the "
                        "cell, e.g. Li16 O600 P16 F96 C600 H600"
                    ),
                    "title": "Cell Formula",
                    "type": "string",
                },
            },
            "required": ["radius", "pair_title", "RDF", "cell_volume", "cell_formula"],
            "title": "RDFOutput",
            "type": "object",
        },
        "RunInfo": {
            "description": (
                "Metadata for a run of a method. This information may "
                "apply to all samples\n    processed in the respective "
                "run.\n    "
            ),
            "properties": {
                "formulation": {
                    "description": (
                        "This is a formulation defining the Chemicals "
                        "contained in thesample and their fraction in the"
                        " total mixture."
                    ),
                    "items": {"$ref": "#/$defs/FormulationComponent"},
                    "title": "Formulation",
                    "type": "array",
                },
                "internal_reference": {
                    "description": (
                        "This field is an internal ID identifying this "
                        "run of the method. In experimental setups, this "
                        "may reference to an ID of the sample."
                    ),
                    "title": "Internal Reference",
                    "type": "string",
                },
                "formulation_info": {
                    "anyOf": [{"$ref": "#/$defs/FormulationInfo"}, {"type": "null"}],
                    "description": (
                        "This is the metadata concerning the formulation "
                        "relevant for documentation."
                    ),
                },
                "chemicals_info": {
                    "anyOf": [
                        {
                            "additionalProperties": {"$ref": "#/$defs/ChemicalInfo"},
                            "type": "object",
                        },
                        {"type": "null"},
                    ],
                    "description": (
                        "This is a dictionary of metadata of the chemicals "
                        "relevant for documentation. The keys are "
                        "InChIKeys of the chemicals contained in the "
                        "formulation and the values are ChemicalInfo "
                        "objects."
                    ),
                    "title": "Chemicals Info",
                },
            },
            "required": [
                "formulation",
                "internal_reference",
                "formulation_info",
                "chemicals_info",
            ],
            "title": "RunInfo",
            "type": "object",
        },
    }

    template_target_list_of_lists = {
        "conductivity-molecular_dynamics": {
            "input_template": {
                "formulation": [
                    {
                        "chemical": {
                            "SMILES": "required, str",
                            "InChIKey": "required, str",
                        },
                        "fraction": "required, float",
                        "fraction_type": "required, str",
                    }
                ],
                "temperature": "optional, float",
            },
            "output_template": {
                "run_info": {
                    "formulation": [
                        {
                            "chemical": {
                                "SMILES": "required, str",
                                "InChIKey": "required, str",
                            },
                            "fraction": "required, float",
                            "fraction_type": "required, str",
                        }
                    ],
                    "internal_reference": "required, str",
                    "formulation_info": (
                        "optional, {'name': 'optional, str', 'uuid': "
                        "'optional, str', 'preparation_date': "
                        "'optional, str', 'batch': 'optional, str', "
                        "'location': \"optional, {'address': "
                        "'required, str', 'detail_1': 'optional, str',"
                        " 'detail_2': 'optional, str'}\"}"
                    ),
                    "chemicals_info": (
                        "optional, {'required, str': {'name': "
                        "'optional, str', 'molar_mass': \"optional, "
                        "('float', 'float')\", 'density': \"optional, "
                        "('float', 'float')\", 'batch': 'optional, str'"
                        ", 'manufacturer': 'optional, str', "
                        "'manufacturing_date': 'optional, str'}}"
                    ),
                },
                "conductivity": {
                    "values": ["required, float"],
                    "temperature": "optional, float",
                    "meta": {"success": "required, bool", "rating": "required, int"},
                },
                "density": (
                    "optional, {'values': ['required, float'], 'temperature': "
                    "'optional, float', 'meta': {'success': 'required, bool', "
                    "'rating': 'required, int'}}"
                ),
                "RDF": (
                    "optional, {'radius': ['required, float'], 'pair_title': "
                    "['required, str'], 'RDF': [['required, float']], "
                    "'cell_volume': 'required, float', 'cell_formula': "
                    "'required, str'}"
                ),
                "number_molecules_per_component": "optional, int",
            },
        }
    }
    # The list of lists is in
    # template_target_list_of_lists["conductivity-molecular_dynamics"]["RDF"]["RDF"]

    template_target_list_of_lists = {
        "run_info": {
            "formulation": [
                {
                    "chemical": {
                        "SMILES": "required, str",
                        "InChIKey": "required, str",
                    },
                    "fraction": "required, float",
                    "fraction_type": "required, str",
                }
            ],
            "internal_reference": "required, str",
            "formulation_info": (
                "optional, {'name': 'optional, str', 'uuid': "
                "'optional, str', 'preparation_date': "
                "'optional, str', 'batch': 'optional, str', "
                "'location': \"optional, {'address': 'required, str', "
                "'detail_1': 'optional, str', 'detail_2': 'optional, "
                "str'}\"}"
            ),
            "chemicals_info": (
                "optional, {'required, str': {'name': 'optional, str', "
                "'molar_mass': \"optional, ('float', 'float')\", "
                "'density': \"optional, ('float', 'float')\", 'batch': "
                "'optional, str', 'manufacturer': 'optional, str', "
                "'manufacturing_date': 'optional, str'}}"
            ),
        },
        "conductivity": {
            "values": ["required, float"],
            "temperature": "optional, float",
            "meta": {"success": "required, bool", "rating": "required, int"},
        },
        "density": (
            "optional, {'values': ['required, float'], 'temperature': "
            "'optional, float', 'meta': {'success': 'required, bool', "
            "'rating': 'required, int'}}"
        ),
        "RDF": (
            "optional, {'radius': ['required, float'], 'pair_title': "
            "['required, str'], 'RDF': [['required, float']], 'cell_volume': "
            "'required, float', 'cell_formula': 'required, str'}"
        ),
        "number_molecules_per_component": "optional, int",
    }

    assert (
        parse_schema_for_template(
            schema=schema_list_of_lists, definitions=definitions_list_of_lists
        )
        == template_target_list_of_lists
    )


# Test to fix of the issue, that a "prefixItems" key is not found
def test_prefix_items():
    schema_prefix = {
        "$defs": {
            "BatteryChemistry": {
                "description": "A description of the chemistry of a cell.\n    ",
                "properties": {
                    "electrolyte": {
                        "description": (
                            "The definition of the composition of the "
                            "electrolyte used in the cells, for which "
                            "the prediction shall be made"
                        ),
                        "items": {"$ref": "#/$defs/FormulationComponent"},
                        "title": "Electrolyte",
                        "type": "array",
                    },
                    "anode": {
                        "allOf": [{"$ref": "#/$defs/Electrode"}],
                        "description": "The definition of the anode.",
                    },
                    "cathode": {
                        "allOf": [{"$ref": "#/$defs/Electrode"}],
                        "description": "The definition of the cathode.",
                    },
                },
                "required": ["electrolyte", "anode", "cathode"],
                "title": "BatteryChemistry",
                "type": "object",
            },
            "Chemical": {
                "description": "Subclass",
                "properties": {
                    "SMILES": {
                        "description": "A SMILES string representing the chemical.",
                        "title": "Smiles",
                        "type": "string",
                    },
                    "InChIKey": {
                        "description": (
                            "The hashed standard International Chemical "
                            "Identifier of the chemical to ensure "
                            "machine-readability."
                        ),
                        "title": "Inchikey",
                        "type": "string",
                    },
                },
                "required": ["SMILES", "InChIKey"],
                "title": "Chemical",
                "type": "object",
            },
            "Electrode": {
                "description": (
                    "The definition of an electrode.\n\n    "
                    ":param BaseModel: _description_\n    "
                    ":type BaseModel: _type_\n    "
                ),
                "properties": {
                    "material": {
                        "description": (
                            "The description of the composition " "of the electrode."
                        ),
                        "items": {"$ref": "#/$defs/FormulationComponent"},
                        "title": "Material",
                        "type": "array",
                    },
                    "mass_loading": {
                        "anyOf": [{"type": "number"}, {"type": "null"}],
                        "description": (
                            "The capacity per unit area of the electrode. "
                            "Unit: milliampere_hour / centimeter ** 2"
                        ),
                        "title": "Mass Loading",
                        "unit": "milliampere_hour / centimeter ** 2",
                    },
                    "size": {
                        "anyOf": [{"type": "number"}, {"type": "null"}],
                        "description": (
                            "The area of the electrode, which is cut "
                            "to a circular shape."
                        ),
                        "title": "Size",
                        "unit": "centimeter ** 2",
                    },
                },
                "required": ["material", "mass_loading", "size"],
                "title": "Electrode",
                "type": "object",
            },
            "FormulationComponent": {
                "description": (
                    "This class shall be used when referring to "
                    "chemicals as a component in a formulation.\n    "
                    "When assembling a formulation based on "
                    "FormulationComponents, consider, that it\n    "
                    "might be required to use the same fraction type "
                    "for all the chemicals.\n    "
                ),
                "properties": {
                    "chemical": {
                        "allOf": [{"$ref": "#/$defs/Chemical"}],
                        "description": (
                            "The chemical, which shall be described as "
                            "a component in a solution ."
                        ),
                    },
                    "fraction": {
                        "description": (
                            "The unitless fraction of the chemical in "
                            "the total of the mixture."
                        ),
                        "title": "Fraction",
                        "type": "number",
                    },
                    "fraction_type": {
                        "description": (
                            "A string defining, what kind of a fraction "
                            "is given in the formulation. This can be for "
                            "example molar fractions, volume fractions, "
                            "mass fractions,.... At the moment only molar "
                            "fractions are supported."
                        ),
                        "title": "Fraction Type",
                        "type": "string",
                    },
                },
                "required": ["chemical", "fraction", "fraction_type"],
                "title": "FormulationComponent",
                "type": "object",
            },
        },
        "description": (
            "The parameters used by the following method\n    "
            "'degradationEOL' - degradationModel\n\n    "
            ":param BaseModel: _description_\n    "
            ":type BaseModel: _type_\n    "
        ),
        "properties": {
            "chemistry": {
                "allOf": [{"$ref": "#/$defs/BatteryChemistry"}],
                "description": (
                    "The description of the chemicals involved in "
                    "all the battery cell."
                ),
            },
            "input_cycles": {
                "anyOf": [
                    {"items": {"type": "number"}, "type": "array"},
                    {"type": "null"},
                ],
                "description": (
                    "The number of cycles provided as " "an input to the model."
                ),
                "title": "Input Cycles",
            },
            "average_charging_rate": {
                "anyOf": [{"type": "number"}, {"type": "null"}],
                "description": (
                    "The average C-rate used for charging of the cell "
                    "in the cycles provided as an input. Unit: 1 / hour"
                ),
                "title": "Average Charging Rate",
                "unit": "1 / hour",
            },
            "maximum_charging_rate": {
                "anyOf": [{"type": "number"}, {"type": "null"}],
                "description": (
                    "The maximum C-rate used for charging of the "
                    "cell in the cycles provided as an input. "
                    "Unit: 1 / hour"
                ),
                "title": "Maximum Charging Rate",
                "unit": "1 / hour",
            },
            "minimum_charging_rate": {
                "anyOf": [{"type": "number"}, {"type": "null"}],
                "description": (
                    "The minimum C-rate used for charging of the cell "
                    "in the cycles provided as an input. Unit: 1 / hour"
                ),
                "title": "Minimum Charging Rate",
                "unit": "1 / hour",
            },
            "delta_coulombic_efficiency": {
                "anyOf": [{"type": "number"}, {"type": "null"}],
                "description": (
                    "The difference in coulombic efficiency " "between cycle x and 10."
                ),
                "title": "Delta Coulombic Efficiency",
            },
            "voltage_gap_charge_discharge": {
                "anyOf": [{"type": "number"}, {"type": "null"}],
                "description": (
                    "The difference of the voltage gap between charge "
                    "and discharge between cycle x and 10. Unit: volt"
                ),
                "title": "Voltage Gap Charge Discharge",
                "unit": "volt",
            },
            "capacity_vector_variance": {
                "anyOf": [{"type": "number"}, {"type": "null"}],
                "description": (
                    "The variance of the difference between the Q(V) "
                    "curves between cycle x and 10."
                ),
                "title": "Capacity Vector Variance",
            },
        },
        "required": [
            "chemistry",
            "input_cycles",
            "average_charging_rate",
            "maximum_charging_rate",
            "minimum_charging_rate",
            "delta_coulombic_efficiency",
            "voltage_gap_charge_discharge",
            "capacity_vector_variance",
        ],
        "title": "DegradationModelInput",
        "type": "object",
    }

    definitions_prefix = {
        "BatteryChemistry": {
            "description": "A description of the chemistry of a cell.\n    ",
            "properties": {
                "electrolyte": {
                    "description": (
                        "The definition of the composition of the "
                        "electrolyte used in the cells, for which the "
                        "prediction shall be made"
                    ),
                    "items": {"$ref": "#/$defs/FormulationComponent"},
                    "title": "Electrolyte",
                    "type": "array",
                },
                "anode": {
                    "allOf": [{"$ref": "#/$defs/Electrode"}],
                    "description": "The definition of the anode.",
                },
                "cathode": {
                    "allOf": [{"$ref": "#/$defs/Electrode"}],
                    "description": "The definition of the cathode.",
                },
            },
            "required": ["electrolyte", "anode", "cathode"],
            "title": "BatteryChemistry",
            "type": "object",
        },
        "Chemical": {
            "description": "Subclass",
            "properties": {
                "SMILES": {
                    "description": "A SMILES string representing the chemical.",
                    "title": "Smiles",
                    "type": "string",
                },
                "InChIKey": {
                    "description": (
                        "The hashed standard International Chemical "
                        "Identifier of the chemical to ensure "
                        "machine-readability."
                    ),
                    "title": "Inchikey",
                    "type": "string",
                },
            },
            "required": ["SMILES", "InChIKey"],
            "title": "Chemical",
            "type": "object",
        },
        "Electrode": {
            "description": (
                "The definition of an electrode.\n\n    :param BaseModel:"
                " _description_\n    :type BaseModel: _type_\n    "
            ),
            "properties": {
                "material": {
                    "description": (
                        "The description of the composition of " "the electrode."
                    ),
                    "items": {"$ref": "#/$defs/FormulationComponent"},
                    "title": "Material",
                    "type": "array",
                },
                "mass_loading": {
                    "anyOf": [{"type": "number"}, {"type": "null"}],
                    "description": (
                        "The capacity per unit area of the electrode. "
                        "Unit: milliampere_hour / centimeter ** 2"
                    ),
                    "title": "Mass Loading",
                    "unit": "milliampere_hour / centimeter ** 2",
                },
                "size": {
                    "anyOf": [{"type": "number"}, {"type": "null"}],
                    "description": (
                        "The area of the electrode, which is cut to a "
                        "circular shape."
                    ),
                    "title": "Size",
                    "unit": "centimeter ** 2",
                },
            },
            "required": ["material", "mass_loading", "size"],
            "title": "Electrode",
            "type": "object",
        },
        "FormulationComponent": {
            "description": (
                "This class shall be used when referring to chemicals as a"
                " component in a formulation.\n    When assembling a "
                "formulation based on FormulationComponents, consider, "
                "that it\n    might be required to use the same fraction "
                "type for all the chemicals.\n    "
            ),
            "properties": {
                "chemical": {
                    "allOf": [{"$ref": "#/$defs/Chemical"}],
                    "description": (
                        "The chemical, which shall be described as a"
                        " component in a solution ."
                    ),
                },
                "fraction": {
                    "description": (
                        "The unitless fraction of the chemical "
                        "in the total of the mixture."
                    ),
                    "title": "Fraction",
                    "type": "number",
                },
                "fraction_type": {
                    "description": (
                        "A string defining, what kind of a fraction is given"
                        " in the formulation. This can be for example molar fractions,"
                        " volume fractions, mass fractions,.... At the moment only "
                        "molar fractions are supported."
                    ),
                    "title": "Fraction Type",
                    "type": "string",
                },
            },
            "required": ["chemical", "fraction", "fraction_type"],
            "title": "FormulationComponent",
            "type": "object",
        },
    }

    template_target_prefix = {
        "chemistry": {
            "electrolyte": [
                {
                    "chemical": {
                        "SMILES": "required, str",
                        "InChIKey": "required, str",
                    },
                    "fraction": "required, float",
                    "fraction_type": "required, str",
                }
            ],
            "anode": {
                "material": [
                    {
                        "chemical": {
                            "SMILES": "required, str",
                            "InChIKey": "required, str",
                        },
                        "fraction": "required, float",
                        "fraction_type": "required, str",
                    }
                ],
                "mass_loading": "optional, float",
                "size": "optional, float",
            },
            "cathode": {
                "material": [
                    {
                        "chemical": {
                            "SMILES": "required, str",
                            "InChIKey": "required, str",
                        },
                        "fraction": "required, float",
                        "fraction_type": "required, str",
                    }
                ],
                "mass_loading": "optional, float",
                "size": "optional, float",
            },
        },
        "input_cycles": "optional, ['required, float']",
        "average_charging_rate": "optional, float",
        "maximum_charging_rate": "optional, float",
        "minimum_charging_rate": "optional, float",
        "delta_coulombic_efficiency": "optional, float",
        "voltage_gap_charge_discharge": "optional, float",
        "capacity_vector_variance": "optional, float",
    }

    assert (
        parse_schema_for_template(schema=schema_prefix, definitions=definitions_prefix)
        == template_target_prefix
    )
