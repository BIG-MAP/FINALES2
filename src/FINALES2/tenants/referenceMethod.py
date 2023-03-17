from typing import Any

import numpy as np

from FINALES2.server.schemas import Result

# Running the methods


def run_my_method(method: str, parameters: dict):
    if method == "DummyMethod":
        quant, res, actualParams = myDummyMethod(parameters=parameters)
    report = {
        "quantity": quant,
        "quantityValue": res,
        "method": method,
        "actualParameters": actualParams,
    }
    return report


def myDummyMethod(parameters: dict):
    params = list(parameters.values())
    print("This is a dummy function returning a float value!")
    # Schwefel function
    params = 1000 * np.array(params) - 500  # rescale onto [-500, 500]
    result = 0
    for index, element in enumerate(params):
        result += -element * np.sin(np.sqrt(np.abs(element)))
    quantity = "DummyQuantity"
    value = (result / 1000 + 0.9816961774673698) / 2.4888170198376653
    actualParams = {"temperature": 15}
    return quantity, value, actualParams


# Preparing the results for posting


def prepare_my_result(request: dict, data: Any) -> Result:
    method = data["method"]
    if method == "DummyMethod":
        formattedResult = prepare_data_from_dummy_method(request=request, data=data)
    return formattedResult


def prepare_data_from_dummy_method(request: dict, data: Any):
    data1 = data
    postResult = Result(
        data={data1["quantity"]: data1["quantityValue"]},
        quantity=data1["quantity"],
        method=[data1["method"]],
        parameters=data1["actualParameters"],
        request_uuid=request["uuid"],
        tenant_uuid="1ecd8115-5506-4b1e-b745-fc08fb2bcaee",
    )

    postResultDict = postResult.__dict__
    return postResultDict
