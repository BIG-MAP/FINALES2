import typing as ty

import jsonschema
import pytest
from pydantic import BaseModel

from FINALES2.engine.server_manager import limitations_schema_translation


@pytest.fixture(scope="module")
def capability_schema():
    """Returns the schema of the capability."""

    class TestSubmodel(BaseModel):
        formula: str
        concentration: float

    class TestModel(BaseModel):
        temperature: int
        unit: str
        options: ty.Dict[str, ty.Union[bool, int]]
        compounds: ty.List[TestSubmodel]

    return TestModel.schema()


class TestLimitationsSchemaTranslation:
    """Tests for the `limitations_schema_translation` method."""

    def test_empty_limitations(self, capability_schema):
        """Test empty limitations."""
        limitations = [{}]
        limitations_schema = limitations_schema_translation(
            capability_schema, capability_schema
        )
        jsonschema.validate(instance=limitations, schema=limitations_schema)

    def test_numeric_ranges(self, capability_schema):
        """Test partial numeric ranges."""
        limitations = [{"temperature": [{"max": 400, "step": 2}, 0]}]
        limitations_schema = limitations_schema_translation(
            capability_schema, capability_schema
        )
        jsonschema.validate(instance=limitations, schema=limitations_schema)

    def test_high_level_conditions(self, capability_schema):
        """Test contitions that apply over several properties."""
        limitations = [
            {"temperature": [{"min": 200, "max": 400, "step": 2}], "unit": ["Kelvin"]},
            {"temperature": [{"min": -73, "max": 273, "step": 2}], "unit": ["Celcius"]},
        ]
        limitations_schema = limitations_schema_translation(
            capability_schema, capability_schema
        )
        jsonschema.validate(instance=limitations, schema=limitations_schema)

    def test_subobject_limitations(self, capability_schema):
        """Test limitations that apply to sub-objects."""
        compound1 = {"formula": ["H2O"], "concentration": [0.8]}
        compound2 = {"formula": ["CH3CH2OH"], "concentration": [0.2]}
        compound3 = {"formula": ["C6H14"], "concentration": [0.4]}
        limitations = [
            {
                "temperature": [{"min": 100, "max": 300, "step": 2}],
                "unit": ["Kelvin"],
                "compounds": [[compound1, compound2], [compound2, compound3]],
            },
        ]
        limitations_schema = limitations_schema_translation(
            capability_schema, capability_schema
        )
        jsonschema.validate(instance=limitations, schema=limitations_schema)

    @pytest.mark.parametrize(
        "limitations",
        [
            # Wrong type in defined value
            [{"temperature": ["string", 0]}],
            # Wrong type in new min specs for a range
            [{"temperature": [{"min": "string"}, 0]}],
            # Wrong key in definition of a range
            [{"temperature": [{"minimum": "string"}, 0]}],
            # Arrays should receive arrays of arrays, not just arrays
            [
                {
                    "compounds": [
                        {"formula": ["H2O"], "concentration": [0.8]},
                        {"formula": ["CH3CH2OH"], "concentration": [0.2]},
                        {"formula": ["C6H14"], "concentration": [0.4]},
                    ],
                }
            ],
        ],
    )
    def test_incorrect_limitations(self, limitations, capability_schema):
        """Test that the code raises with incorrect limitations."""
        limitations_schema = limitations_schema_translation(
            capability_schema, capability_schema
        )
        with pytest.raises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(instance=limitations, schema=limitations_schema)
