import json
import time
from datetime import datetime
from typing import Any, Callable, Optional

import requests
from pydantic import BaseModel

from FINALES2.schemas import GeneralMetaData, Method, Quantity, ServerConfig
from FINALES2.server.schemas import Request
from FINALES2.user_management.classes_user_manager import User


class Tenant(BaseModel):
    """A class to represent a tenant for a FINALES run.

    :param BaseModel: The BaseModel of pydantic is used to provide type checking
    :type BaseModel: pydantic.BaseModel
    :return: An instance of a tenant object
    :rtype: Tenant
    """

    general_meta: GeneralMetaData
    quantities: dict[str, Quantity]
    queue: list = []
    sleep_time_s: int = 1
    tenant_config: Any
    run_method: Callable
    prepare_results: Callable
    FINALES_server_config: ServerConfig
    end_run_time: Optional[datetime]
    authorization_header: Optional[dict]
    operator: User
    tenant_user: User
    tenant_uuid: str

    def to_json(self) -> str:
        """A function to create a JSON string from a tenant object

        :return: A JSON string containing all the information in the fields of the
                 tenant object
        :rtype: str
        """
        return self.json()

    # TODO: Consider changing this function using pydantic parse_obj_as
    # (https://docs.pydantic.dev/latest/usage/models/#parsing-data-into-a-specified-type)
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
            if k == "general_meta":
                attrsJSON[k] = GeneralMetaData(**attr)
            if k in ["operator", "tenant_user"]:
                attrsJSON[k] == User(**attr)
            if k == "quantities":
                # TODO: properly deserialize the methods
                for qKey in attr.keys():
                    methods = {}
                    for key in attr[qKey]["methods"]:
                        methods[key] = Method(**attr[qKey]["methods"][key])
                    attr[qKey]["methods"] = methods
                    attrsJSON[k][qKey] = Quantity(**attr[qKey])
            if k == "end_run_time":
                attrsJSON[k] = datetime.fromisoformat(attr)
            if k == "queue":
                attrsJSON[k] = eval(attr)
        tenantObj = Tenant(**attrsJSON)
        return tenantObj

    def _login(func: Callable):
        # Impelemented using this tutorial as an example:
        # https://realpython.com/primer-on-python-decorators/#is-the-user-logged-in
        def _login_func(self, *args, **kwargs):
            print("Logging in ...")
            access_information = requests.post(
                (
                    f"http://{self.FINALES_server_config.host}:"
                    f"{self.FINALES_server_config.port}/user_management/authenticate/"
                ),
                data={
                    "grant_type": "",
                    "username": f"{self.tenant_user.username}",
                    "password": f"{self.tenant_user.password}",
                    "scope": "",
                    "client_id": "",
                    "client_secret": "",
                },
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            access_information = access_information.json()
            self.authorization_header = {
                "accept": "application/json",
                "Authorization": (
                    f"{access_information['token_type'].capitalize()} "
                    f"{access_information['access_token']}"
                ),
            }
            return func(self, *args, **kwargs)

        return _login_func

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
            if isinstance(requestParameters[p], float) or isinstance(
                requestParameters[p], int
            ):
                tenantMin = methodForQuantity.limitations[p][0]
                tenantMax = methodForQuantity.limitations[p][1]
                minimumOK = requestParameters[p] > tenantMin
                maximumOK = requestParameters[p] < tenantMax
                parametersCheck.append(minimumOK and maximumOK)
        parametersOK: bool = all(parametersCheck)
        return parametersOK

    @_login
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
        print("Looking for tasks ...")
        # get the pending requests from the FINALES server
        pendingRequests = requests.get(
            f"http://{self.FINALES_server_config.host}"
            f":{self.FINALES_server_config.port}/pending_requests/",
            params={},
            headers=self.authorization_header,
        )
        return pendingRequests.json()

    # TODO: implement these functions once there is an example case, where it needs
    # to be applied.
    def _post_request(self):
        pass

    # TODO: implement these functions once there is an example case, where it needs
    # to be applied.
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
        result_formatted.tenant_uuid = self.tenant_uuid
        result_formatted = result_formatted.dict()

        # post the result
        _postedResult = requests.post(
            f"http://{self.FINALES_server_config.host}"
            f":{self.FINALES_server_config.port}/results/",
            json=result_formatted,
            params={},
            headers=self.authorization_header,
        )
        _postedResult.raise_for_status()
        print(f"Result is posted {_postedResult.json()}!")

        # delete the request from the queue
        self.queue.remove(request)
        requestUUID = request["uuid"]
        print(f"Removed request with UUID {requestUUID} from the queue.")

    def _run_method(self, method: str, parameters: dict[str, Any]):
        print("Running method ...")
        return self.run_method(method, parameters)

    def _prepare_results(self, request: dict, data: Any):
        print("Preparing results ...")
        return self.prepare_results(request, data)

    def run(self):
        """This function runs the tenant in a loop - getting all the requests from
        the server, checking them for their compatibility with the tenant and posting
        them to the server.
        """
        # run until the end_run_time is exceeded
        # this is intended for maintenance like refilling consumables,
        # for which a time can roughly be estimated
        while datetime.now() < self.end_run_time:
            # wait in between two requests to the server
            time.sleep(self.sleep_time_s)
            self._update_queue()
            if len(self.queue) > 0:
                # get the first request in the queue to work on -> first in - first out
                activeRequest = self.queue[0]
                # strip the metadata from the request
                activeRequest_technical = Request(**activeRequest["request"])

                # extract the method and the parameters from the request
                reqMethod = activeRequest_technical.methods[0]
                reqParameters = activeRequest_technical.parameters[reqMethod]

                # get the method, which matches
                resultData = self._run_method(
                    method=reqMethod, parameters=reqParameters
                )
                # post the result
                self._post_result(request=activeRequest, data=resultData)
            continue
