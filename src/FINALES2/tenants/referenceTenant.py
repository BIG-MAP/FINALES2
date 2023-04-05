import json
import time
from datetime import datetime
from typing import Any, Callable, Optional
from uuid import UUID

import requests
from pydantic import BaseModel

import FINALES2.server.config as config
from FINALES2.schemas import GeneralMetaData, Method, Quantity, ServerConfig, User
from FINALES2.server.schemas import Request


class Tenant(BaseModel):
    """A class to represent a tenant for a FINALES run.

    :param BaseModel: The BaseModel of pydantic is used to provide type checking
    :type BaseModel: pydantic.BaseModel
    :return: An instance of a tenant object
    :rtype: Tenant
    """

    generalMeta: GeneralMetaData
    quantities: dict[str, Quantity]
    queue: list = []
    tenantConfig: Any
    _run_method: Callable
    _prepare_results: Callable
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
            elif isinstance(attrObj, dict):
                if isinstance(attrObj[list(attrObj.keys())[0]], Quantity):
                    # convert each element in the list to a dictionary seperately
                    for quantityKey in attrObj.keys():
                        quantityDict = attrObj[quantityKey].__dict__
                        methodsDict = quantityDict["methods"].copy()
                        for method in methodsDict.keys():
                            methodsDict[method] = methodsDict[method].__dict__
                        quantityDict["methods"] = methodsDict
                        tenantDict[attr][quantityKey] = quantityDict
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
            elif isinstance(attrObj, list):
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
                for qKey in attr.keys():
                    methods = {}
                    for key in attr[qKey]["methods"]:
                        methods[key] = Method(**attr[qKey]["methods"][key])
                    attr[qKey]["methods"] = methods
                    attrsJSON[k][qKey] = Quantity(**attr[qKey])
            if k == "endRuntime":
                attrsJSON[k] = datetime.fromisoformat(attr)
            if k == "queue":
                attrsJSON[k] = eval(attr)
        tenantObj = Tenant(**attrsJSON)
        return tenantObj

    def _checkQuantity(self, request: Request) -> bool:
        """This function checks, if a quantity in a request can be provided by the
        tenant.

        :param request: a request object, which contains all the information relevant
        to the execution of the request
        :type request: Request
        :return: a boolean value stating, whether the requested quantity can be
        provided by the tenant
        :rtype: bool
        """
        requestedQuantity = request.quantity
        tenantQuantitites = self.quantities.keys()
        return requestedQuantity in tenantQuantitites

    def _checkMethods(self, request: Request, requestedQuantity: str) -> list[str]:
        """This function checks the methods in the request, if they are available in
        from the tenant and returns the names of the matching methods in a list.

        :param request: the requrest, which needs to be checked for feasibility
        :type request: Request
        :param requestedQuantity: the quantity, which shall be determined
        :type requestedQuantity: str
        :return: a list of the names of the methods, which can be performed by the
        tenant and are requested in the request
        :rtype: list[str]
        """
        tenantMethods = self.quantities[requestedQuantity].methods.keys()
        requestedMethods = request.methods
        # Collect all the matching methods in case the parameters are out of range
        # for the first method found.
        matchingMethods = []
        for method in requestedMethods:
            if method in tenantMethods:
                matchingMethods.append(method)
        return matchingMethods

    def _checkParameters(self, request: Request, method: str) -> bool:
        """This function checks the requested parameters for their compatibility
        with the tenant.

        :param request: a request containing the parameters to use when processing
        the request
        :type request: Request
        :param method: the method already identified as being compatible between the
        request and the tenant
        :type method: str
        :return: a boolean indicating, whether the parameters of the request are
        within the limitations of the tenant (True) or not (False)
        :rtype: bool
        """
        parametersCheck = []
        requestParameters = request.parameters[method]
        methodForQuantity = self.quantities[request.quantity].methods[method]
        for p in requestParameters.keys():
            tenantMin = methodForQuantity.limitations[p]["minimum"]
            tenantMax = methodForQuantity.limitations[p]["maximum"]
            minimumOK = requestParameters[p] > tenantMin
            maximumOK = requestParameters[p] < tenantMax
            parametersCheck.append(minimumOK and maximumOK)
        parametersOK: bool = all(parametersCheck)
        return parametersOK

    def _update_queue(self) -> None:
        """This function clears and recreates the queue of the tenant."""
        # empty the queue before recreating it to make sure, that all the requests
        # listed in the queue are still pending and were not worked on by another
        # tenant
        self.queue.clear

        # get the pending requests from the FINALES server
        pendingRequests = self._get_pending_requests()

        # update the queue of the tenant

        for pendingItem in pendingRequests:
            # create the Request object from the json string
            requestDict = pendingItem["request"]
            request = Request(**requestDict)

            # check, if the pending request fits with the tenant
            # check the quantity matches
            if not self._checkQuantity(request=request):
                continue

            # check, if the methods match with the tenant methods
            # This overwrites the request object. If an appropriate method was found
            # for the tenant, the methods list of the returned request only contains
            # the found method. Otherwise, the returned request is unchanged to the
            # original one
            matchedMethods = self._checkMethods(
                request=request, requestedQuantity=request.quantity
            )
            if matchedMethods == []:
                continue

            # check, if the parameters match with the tenant method
            for method in matchedMethods:
                if self._checkParameters(request=request, method=method):
                    request.methods = [method]
                    break

            # Reassemble the pendingItem to collect the full request in the queue with
            # only the method changed to the one, which can be performed by the tenant
            pendingItem["request"] = request.__dict__

            self.queue.append(pendingItem)

    def _get_pending_requests(self) -> list[dict]:
        """This funciton collecte all the pending requests from the server.

        :return: a list of requests in JSON format
        :rtype: list[dict]
        """
        # login to the server
        print("Logging in ...")
        requests.post(
            (
                f"http://{self.FINALESServerConfig.host}:"
                f"{self.FINALESServerConfig.port}/userManagement/authenticate/"
            ),
            data={
                "grant_type": "",
                "username": f"{self.tenantUser.username}",
                "password": f"{self.tenantUser.password}",
                "scope": "",
                "client_id": "",
                "client_secret": "",
            },
            params={
                "userDB": f"{config.userDB}",
            },
            headers={
                "accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
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
        """This function posts a result generated in reply to a request.

        :param request: a request specifying the details of the requested data
        :type request: Request
        :param data: the data generated while serving the request
        :type data: Any
        """
        # transfer the output of your method to a postable result
        result_formatted = self._prepare_results(request=request, data=data)

        # post the result
        _postedResult = requests.post(
            f"http://{self.FINALESServerConfig.host}"
            f":{self.FINALESServerConfig.port}/post/result/",
            json=result_formatted,
            params={},
            headers={}
            # headers=accessInfo.json(),
        )
        _postedResult.raise_for_status()
        print(f"Result is posted {_postedResult.json()}!")

        # delete the request from the queue
        self.queue.remove(request)
        requestUUID = request["uuid"]
        print(f"Removed request with UUID {requestUUID} from the queue.")

    def run(self):
        """This function runs the tenant in a loop - getting all the requests from
        the server, checking them for their compatibility with the tenant and posting
        them to the server.
        """
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
