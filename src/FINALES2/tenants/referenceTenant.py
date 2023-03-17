import json
import time
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

import requests

# import uvicorn
from pydantic import BaseModel

import FINALES2.server.config as config
from FINALES2.schemas import GeneralMetaData, Quantity, ServerConfig, User
from FINALES2.server.schemas import Request
from FINALES2.tenants.referenceMethod import prepare_my_result, run_my_method


class Tenant(BaseModel):
    """A class to represent a tenant for a FINALES run.

    :param BaseModel: The BaseModel of pydantic is used to provide type checking
    :type BaseModel: pydantic.BaseModel
    :return: The instatiation returns an tenant object
    :rtype: Tenant
    """

    generalMeta: GeneralMetaData
    quantities: dict[str, Quantity]
    queue: list = []
    tenantConfig: Any
    FINALESServerConfig: ServerConfig
    endRuntime: Optional[datetime]
    operator: User
    tenantUser: User

    # TODO: fix for new types of attributes (methods and quantities)
    # TODO: add tenantConfig object
    def to_json(self) -> str:
        """A function to create a JSON string from a tenant object

        :return: A JSON string containing all the information in the fields of the
                 tenant object
        :rtype: str
        """
        # get the dictionary of the tenant object to know the top level keys
        tenantDict = self.__dict__
        # go through all the attributes of the tenant object
        for attr in tenantDict.keys():
            # get the attribute
            attrObj = getattr(self, attr)
            # if it is of type GeneralMetaData or ServerConfig
            if type(attrObj) in [GeneralMetaData, ServerConfig]:
                # using the dictionary is possible
                tenantDict[attr] = attrObj.__dict__
            # if it is a list of Quantity objects
            elif isinstance(attrObj, list):
                if len(attrObj) > 0:
                    if isinstance(attrObj[0], Quantity):
                        # convert each element in the list to a dictionary seperately
                        tenantDict[attr] = [e.__dict__ for e in attrObj]
                        methodsDict = tenantDict[attr]["methods"].copy()
                        for method in methodsDict.keys():
                            methodsDict[method] = methodsDict[method].__dict__
                        tenantDict[attr]["methods"] = methodsDict
                    else:
                        tenantDict[attr] = str(attrObj)
                else:
                    tenantDict[attr] = str(attrObj)
            # if it is a user
            elif isinstance(attrObj, User):
                # get the top level keys by casting to a dictionary
                tenantDict[attr] = attrObj.__dict__
                # copy this dictionary
                attrDict = tenantDict[attr].copy()
                # iterate over the keys
                for element in tenantDict[attr].keys():
                    # if a UUID is found
                    if isinstance(attrDict[element], UUID):
                        # cast it to a string
                        attrDict[element] = str(tenantDict[attr][element])
                # assign the resulting dictionary to the tenantDict
                tenantDict[attr] = attrDict
            # if it is a datetime object
            elif isinstance(attrObj, datetime):
                # cast the datetime object to a string in iso format
                tenantDict[attr] = attrObj.isoformat()
            elif isinstance(attrObj, list) and not isinstance(attrObj[0], Quantity):
                # cast the list object to a string
                tenantDict[attr] = str(attrObj)
        # format the tenantDict as a JSON string
        return json.dumps(tenantDict)

    def from_json(attrsStr: str):
        """A function to obtain a tenant object from a JSON string

        :param attrsStr: The JSON string, which shall be converted to a tenant object
        :type attrsStr: str
        :return: The tenant object based on the entries of the input JSON string
        :rtype: Tenant
        """
        # load the JSON string into a JSON object
        attrsJSON = json.loads(attrsStr)
        # get the attributes of the tenant object (in this case, no instance of the
        # class is available and the class definition is used)
        attrsKeys = vars(Tenant)["__fields__"].keys()
        # iterate through the list of attributes
        for k in attrsKeys:
            # get the corresponding entry in the JSON object
            attr = attrsJSON[k]
            # check for each attribute and create the respective object from the
            # dictionary in the JSON object
            if k == "generalMeta":
                attrsJSON[k] = GeneralMetaData(**attr)
            if k in ["operator", "tenantUser"]:
                attrsJSON[k] == User(**attr)
            if k == "quantities":
                # TODO: properly deserialize the methods
                attrsJSON[k] = [Quantity(**q) for q in attr]
            if k == "endRuntime":
                attrsJSON[k] = datetime.fromisoformat(attr)
            if k == "queue":
                attrsJSON[k] = eval(attr)
        # instatiate a tenant bbject based on the resulting dictionary
        tenantObj = Tenant(**attrsJSON)
        # return the tenant object
        return tenantObj

    def _update_queue(self) -> None:
        # get the pending requests from the FINALES server
        pendingRequests = self._get_requests()

        # update the queue of the tenant

        # get the relevant requests
        for pendingItem in pendingRequests:
            # create the Request object from the json string
            requestDict = pendingItem["request"]
            request = Request(**requestDict)

            # check, if the pending request fits with the tenant
            # check the quantity matches
            quantityOK = request.quantity in [q for q in self.quantities.keys()]
            if quantityOK:
                # check methods
                # the tenant at the moment
                tenantMethods: list = []
                for q in self.quantities.keys():
                    tenantMethods.extend(self.quantities[q].methods.keys())
                for method in tenantMethods:
                    if method in request.methods:
                        request.methods = [method]
                        methodOK = True
                    else:
                        methodOK = False
                if methodOK:
                    # check parameters
                    parametersCheck: list = []
                    requestParameters = request.parameters[method]
                    methodForQuantity = self.quantities[request.quantity].methods[
                        request.methods[0]
                    ]
                    for p in requestParameters.keys():
                        tenantMin = methodForQuantity.limitations[p]["minimum"]
                        tenantMax = methodForQuantity.limitations[p]["maximum"]
                        minimumOK = requestParameters[p] > tenantMin
                        maximumOK = requestParameters[p] < tenantMax
                        parametersCheck.append(minimumOK and maximumOK)
                    parametersOK: bool = all(parametersCheck)
            # summarize the checks
            requestOK = quantityOK and methodOK and parametersOK
            # if the request is ok and it is not yet in the tenant's queue
            # add it
            if requestOK and request not in self.queue:
                pendingItem["request"] = request.__dict__
                self.queue.append(pendingItem)

    def _get_requests(self) -> list[Request]:
        # login to the server
        print("Logging in ...")
        # accessInfo = requests.post(
        #     f"http://{self.FINALESServerConfig.host}:"
        #     f"{self.FINALESServerConfig.port}/userManagement/authenticate",
        #     data={},
        #     headers={}
        #     # data={
        #     #     "username": self.tenantUser.username,
        #     #     "password": self.tenantUser.password,
        #     #     "grant_type": "password",
        #     # },
        #     # headers={"content-type": "application/x-www-form-urlencoded"},
        # )
        print("Looking for tasks...")

        # get the pending requests from the FINALES server
        pendingRequests = requests.get(
            f"http://{self.FINALESServerConfig.host}"
            f":{self.FINALESServerConfig.port}/get/pending_requests/",
            params={},
            headers={}
            # headers=accessInfo.json(),
        ).json()
        return pendingRequests

    def _post_request(self):
        pass

    def _get_results(self):
        pass

    def _post_result(self, request: Request, data: Any):
        # transfer the output of your method to a postable result
        result_formatted = prepare_my_result(request=request, data=data)
        print(result_formatted)

        # post the result
        _postedResult = requests.get(
            f"http://{self.FINALESServerConfig.host}"
            f":{self.FINALESServerConfig.port}/post/result/",
            data={result_formatted},
            params={},
            headers={}
            # headers=accessInfo.json(),
        ).json()
        print(f"Result is posted {_postedResult}!")

        # delete the request from the queue
        self.queue.remove(request)
        requestUUID = request["uuid"]
        print(f"Removed request with UUID {requestUUID} from the queue.")

    def _run_method(self, method: str, parameters: dict):
        # TODO: Add the way how you process the input
        result = run_my_method(method=method, parameters=parameters)
        return result

    def run(self):
        # run until the endRuntime is exceeded
        # this is intended for maintenance like refilling consumables,
        # for which a time can roughly be estimated
        while datetime.now() < self.endRuntime:
            # wait in between two requests to the server
            time.sleep(config.sleepTime_s)
            self._update_queue()
            # get the first request in the queue to work on -> first in - first out
            activeRequest = self.queue[0]
            # strip the metadata from the request
            activeRequest_technical = Request(**activeRequest["request"])

            # extract the method and the parameters from the request
            reqMethod = activeRequest_technical.methods[0]
            reqParameters = activeRequest_technical.parameters[reqMethod]

            # get the method, which matches
            resultData = self._run_method(method=reqMethod, parameters=reqParameters)

            # post the result
            self._post_result(request=activeRequest, data=resultData)
            continue
