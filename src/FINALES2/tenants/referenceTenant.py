import json
import time
from datetime import datetime
from typing import Any, Callable, Optional, Union, cast

import requests
from pydantic import BaseModel

from FINALES2.engine.main import RequestStatus, ResultStatus
from FINALES2.schemas import GeneralMetaData, Quantity, ServerConfig
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
    tenant_config: Any = None
    run_method: Callable
    prepare_results: Callable
    FINALES_server_config: ServerConfig
    end_run_time: Optional[datetime] = None
    authorization_header: Optional[dict] = None
    operators: list[User]
    tenant_user: User
    tenant_uuid: str

    def tenant_object_to_json(self):
        """
        Funciton for creating the json input file, which is to be forwarded to the admin
        for registering a tenant.

        The uuid will be returned by the admin, which the user then will add to there
        Tenant object tenant_uuid field.
        """

        limitations = []
        capability_keys = list(self.quantities.keys())
        for capa_key in capability_keys:
            method_keys = list(self.quantities[capa_key].methods.keys())
            for method_key in method_keys:
                limitations.append(
                    {
                        "quantity": capa_key,
                        "method": method_key,
                        "limitations": self.quantities[capa_key]
                        .methods[method_key]
                        .limitations,
                    }
                )

        output_dict = {
            "name": self.general_meta.name,
            "limitations": limitations,
            "contact_person": str([u.username for u in self.operators]),
        }

        with open(f"{self.general_meta.name}_tenant.json", "w") as fp:
            json.dump(output_dict, fp, indent=2)

        return

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
        # TODO: Reactivate this check. This requires a parsing of the input and
        # limitations.
        # parametersCheck = []
        # requestParameters = request.parameters[method]
        # methodForQuantity = self.quantities[request.quantity].methods[method]
        # for p in requestParameters.keys():
        #     if isinstance(requestParameters[p], (float, int)):
        #         if isinstance(methodForQuantity.limitations[p], dict):
        #             tenantMin = methodForQuantity.limitations[p]["min"]
        #             tenantMax = methodForQuantity.limitations[p]["max"]
        #         elif isinstance(methodForQuantity.limitations[p], float):

        #         minimumOK = requestParameters[p] > tenantMin
        #         maximumOK = requestParameters[p] < tenantMax
        #         parametersCheck.append(minimumOK and maximumOK)
        # parametersOK: bool = all(parametersCheck)
        # return parametersOK
        return True

    @_login
    def _change_status(
        self,
        req_res_dict: dict,
        new_status: Union[RequestStatus, ResultStatus],
        status_change_message: Optional[str] = None,
    ):
        """This function changes the status of either a request or a result. It takes
        a dictionary of either a RequestInfo or a ResultInfo object as an input and
        selects the respective endpoint accordingly."""
        if "request" in req_res_dict.keys():
            obj_type = "request"
            if type(new_status) != RequestStatus:
                raise ValueError(
                    f"Wrong status type. The type given is "
                    f"{type(new_status)} instead of RequestStatus."
                )
        elif "result" in req_res_dict.keys():
            obj_type = "result"
            if type(new_status) != ResultStatus:
                raise ValueError(
                    f"Wrong status type. The type given is "
                    f"{type(new_status)} instead of ResultStatus."
                )

        params = {
            "request_id": req_res_dict["uuid"],
            "new_status": new_status.value,
        }
        if status_change_message is not None:
            params["status_change_message"] = status_change_message

        header = cast(dict, self.authorization_header).copy()
        header["Content-Type"] = "application/x-www-form-urlencoded"

        _new_status = requests.post(
            f"http://{self.FINALES_server_config.host}"
            f":{self.FINALES_server_config.port}/"
            f"{obj_type}s/{req_res_dict['uuid']}/update_status/",
            params=params,
            headers=header,
        )
        _new_status.raise_for_status()
        print(f"{req_res_dict['uuid']}: {_new_status.json()}!")

    @_login
    def _update_queue(self) -> None:
        """This function clears and recreates the queue of the tenant."""
        # empty the queue before recreating it to make sure, that all the requests
        # listed in the queue are still pending and were not worked on by another
        # tenant
        self.queue.clear()

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

    @_login
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

    # TODO: implement (input) validations.
    @_login
    def _post_request(
        self,
        quantity: str,
        methods: list[str],
        parameters: dict[str, dict[str, Any]],
    ) -> None:
        """This function posts a request.

        :param quantity: the name of the quantity to be requested
        :type quantity: str
        :param methods: a list of the method names acceptable for creating the result
        :type methods: list[str]
        :param parameters: a dictionary of the parameters, which shall be used when
            running the method; first key is the name of the method, the second level
            keys are the names of the parameters
        :type parameters: dict[str, dict[str, Any]]
        """

        request = Request(
            quantity=quantity,
            methods=methods,
            parameters=parameters,
            tenant_uuid=self.tenant_uuid,
        ).model_dump()

        _posted_request = requests.post(
            f"http://{self.FINALES_server_config.host}"
            f":{self.FINALES_server_config.port}/requests/",
            json=request,
            params={},
            headers=self.authorization_header,
        )
        _posted_request.raise_for_status()
        print(f"Request is posted {_posted_request.json()}!")

    # TODO: implement (input) validations.
    @_login
    def _get_results(
        self,
        quantity: Union[str, None],
        method: Union[str, None],
        request_id: Union[str, None] = None,
    ) -> Union[list, dict]:
        """This function queries requests from the FINALES server. It my either provide
        a list of requests, if quantity and method is given, or a single request, if a
        request_id and optionally quantity and method are given. If there is no
        request_id and either quantity or method is None, a ValueError is raised

        :param quantity: the name of the quantity to be requested
        :type quantity: Union[str,None]
        :param method: the name of the method, by which the result was created
        :type method: Union[str,None]
        :param request_id: the id of the request, which asked for the result,
            defaults to None
        :type request_id: Union[str,None], optional
        :raises ValueError: A value error is raised, if information for requesting
            results by any of the available endpoints is impossible
        :return: _description_
        :rtype: Union[list,dict]
        """
        print("Looking for results ...")
        if request_id is None:
            if (quantity is None) or (method is None):
                raise ValueError(
                    "No request ID was passed, therefore a quantity and method must "
                    "be specified."
                )
            # get the results from the FINALES server
            results = requests.get(
                f"http://{self.FINALES_server_config.host}"
                f":{self.FINALES_server_config.port}/results_requested/",
                params={"quantity": quantity, "method": method},
                headers=self.authorization_header,
            )
            return results.json()
        else:
            if (quantity is not None) or (method is not None):
                raise ValueError(
                    "A request ID was passed, therefore quantity and method must not "
                    "be specified."
                )
            # get the result for this ID from the FINALES server
            result = requests.get(
                f"http://{self.FINALES_server_config.host}"
                f":{self.FINALES_server_config.port}/results_requested/{request_id}",
                params={},
                headers=self.authorization_header,
            )
            return result.json()

    @_login
    def _post_result(self, request: dict, data: Any):
        """This function posts a result generated in reply to a request.

        :param request: a request dictionary specifying the details of the requested
                        data
        :type request: dict
        :param data: the data generated while serving the request
        :type data: Any
        """
        # transfer the output of your method to a postable result
        result_formatted = self._prepare_results(request=request, data=data)
        result_formatted["tenant_uuid"] = self.tenant_uuid

        # post the result
        _posted_result = requests.post(
            f"http://{self.FINALES_server_config.host}"
            f":{self.FINALES_server_config.port}/results/",
            json=result_formatted,
            params={},
            headers=self.authorization_header,
        )
        _posted_result.raise_for_status()
        print(f"Result is posted {_posted_result.json()}!")

        # delete the request from the queue
        self.queue.remove(request)
        requestUUID = request["uuid"]
        if request not in self.queue:
            print(f"Removed request with UUID {requestUUID} from the queue.")
        else:
            print(f"Request with UUID {requestUUID} still in queue!")

    @_login
    def _run_method(self, request_info: dict[str, Any]):
        print("Running method ...")
        # mark the request as "reserved", (cast required to assert mypy, this will be
        # not None, when this is called)
        self._change_status(
            req_res_dict=request_info,
            new_status=RequestStatus.RESERVED,
            status_change_message=f"Reserved for {self.tenant_user.username}.",
        )
        return self.run_method(request_info)

    def _prepare_results(self, request: dict, data: Any) -> dict[str, Any]:
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

                try:
                    # get the method, which matches
                    resultData = self._run_method(request_info=activeRequest)
                    # post the result
                    self._post_result(request=activeRequest, data=resultData)
                # To catch errors during the execution of the method or if the
                # execution is interrupted intentionally by the user
                # using KeyboardInterrupt
                except (Exception, KeyboardInterrupt):
                    self._change_status(
                        req_res_dict=activeRequest,
                        new_status=RequestStatus.PENDING,
                        status_change_message=(
                            f"Processing of request {activeRequest['uuid']} failed."
                        ),
                    )
                    raise
            continue
