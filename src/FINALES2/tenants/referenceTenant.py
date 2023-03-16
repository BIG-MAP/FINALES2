import json
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel

from FINALES2.schemas import GeneralMetaData, Quantity, ServerConfig, User

# import time
# import requests
# import uvicorn
# import FINALES2.server.config as config


# TODO: Import the RestAPI schemas -> remove this once the real schemas are available
class Request(BaseModel):
    quantity: str
    methods: str
    parameters: dict
    tenant_uuid: str


class Tenant(BaseModel):
    """A class to represent a tenant for a FINALES run.

    :param BaseModel: The BaseModel of pydantic is used to provide type checking
    :type BaseModel: pydantic.BaseModel
    :return: The instatiation returns an tenant object
    :rtype: Tenant
    """

    class Config:
        arbitrary_types_allowed = True

    generalMeta: GeneralMetaData
    quantities: list[Quantity]
    queue: Optional[list] = []
    tenantConfig: Any
    FINALESServerConfig: ServerConfig
    endRuntime: Optional[datetime]
    operator: User
    tenantUser: User

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
            elif isinstance(attrObj, list) and isinstance(attrObj[0], Quantity):
                # convert each element in the list to a dictionary seperately
                tenantDict[attr] = [e.__dict__ for e in attrObj]
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
                attrsJSON[k] = [Quantity(**q) for q in attr]
            if k == "endRuntime":
                attrsJSON[k] = datetime.fromisoformat(attr)
        # instatiate a tenant bbject based on the resulting dictionary
        tenantObj = Tenant(**attrsJSON)
        # return the tenant object
        return tenantObj

    # def _updateQueue(self) -> None:
    #     # get the pending requests from the FINALES server
    #     pendingRequests = self._get_requests()
    #     # TODO: Which endpoint to use? What is the return value?

    #     # update the queue of the tenant

    #     # get the relevant requests
    #     for pendingItem in pendingRequests.items:
    #         # create the Request object from the json string
    #         requestDict = json.loads(pendingItem)
    #         request = Request(**requestDict)
    #         # check, if the pending request fits with the tenant
    #         # check the quantity matches
    #         quantityOK = request.quantity in [q.name for q in self.quantities]
    #         if quantityOK:
    #             # check methods
    #             # TODO: There is a limitation to one method per quantity for
    #             # the tenant at the momen
    #             tenantMethods = [q.methods.name for q in self.quantities]
    #             methodOK = any([m in tenantMethods for m in request.methods])
    #             if methodOK:
    #                 # check parameters
    #                 parametersCheck = []
    #                 requestParameters = request.parameters
    #                 for p in requestParameters.keys():
    #                     tenantMin = self.limitations[p]["minimum"]
    #                     tenantMax = self.limitations[p]["maximum"]
    #                     minimumOK = requestParameters[p] > tenantMin
    #                     maximumOK = requestParameters[p] < tenantMax
    #                     parametersCheck.append(minimumOK and maximumOK)
    #                 parametersOK = all(parametersCheck)
    #         # summarize the checks
    #         requestOK = quantityOK and methodOK and parametersOK
    #         # if the request is ok and it is not yet in the tenant's queue
    #         # add it
    #         if requestOK and request not in self.queue:
    #             self.queue.append(request)

    # def _get_requests(self) -> list[Request]:
    #     # # collect the quantity names and methods in a list
    #     # quantityNames = [q.name for q in quantities]
    #     # quantityMethods = [q.method for q in quantities]
    #     # get the pending requests from the FINALES server
    #     pendingRequests = requests.get(
    #         f"http://{self.FINALESServer.config.host}"
    #         ":{self.FINALESServer.config.host}/???",
    #         params={
    #             "quantityNames": quantityNames,
    #             "quantityMethods": quantityMethods,
    #         },
    #         headers=accessInfo,
    #     ).json()
    #     # TODO: Which endpoint to use? What is the return value?

    # def _post_request(self):
    #     pass

    # def _get_results(self):
    #     pass

    # def _post_results(self):
    #     pass

    # def run(self):
    #     # instantiate the FINALES server
    #     FINALESServer = uvicorn.Server(self.FINALESServerConfig)

    #     # run until the endRuntime is exceeded
    #     # this is intended for maintenance like refilling consumables,
    #     # for which a time can roughly be estimated
    #     while datetime.now() < self.endRuntime:
    #         # wait in between two requests to the server
    #         time.sleep(config.sleepTime_s)
    #         # login to the server
    #         print("Logging in ...")
    #         accessInfo = requests.post(
    #             f"http://{FINALESServer.config.host}:"
    #             "{FINALESServer.port}/userManagement/authenticate",
    #             data={
    #                 "username": tenantUser.username,
    #                 "password": tenantUser.password,
    #                 "grant_type": "password",
    #             },
    #             headers={"content-type": "application/x-www-form-urlencoded"},
    #         )
    #         print("Looking for tasks...")

    #         # get the first request in the queue to work on -> first in - first out
    #         activeRequest = self.queue[0]

    #         # TODO: Add the way how you process the input
    #         resultData =
