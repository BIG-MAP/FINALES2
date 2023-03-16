import json
import time
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import requests
import uvicorn
from pydantic import BaseModel

import FINALES2.server.config as config
from FINALES2.schemas import GeneralMetaData, Quantity, ServerConfig, User


class Tenant(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    generalMeta: GeneralMetaData
    operator: User
    quantities: list[Quantity]
    tenantServerConfig: ServerConfig
    FINALESServerConfig: ServerConfig
    endRuntime: Optional[datetime]
    tenantUser: User

    def to_json(self) -> str:
        # jsonCompatibleTypes = [str, list, dict, int, float]
        tenantDict = self.__dict__
        for attr in vars(self):
            if "__" not in attr:
                attrObj = getattr(self, attr)
                if type(attrObj) in [GeneralMetaData, ServerConfig]:
                    tenantDict[attr] = attrObj.__dict__
                elif isinstance(attrObj, list) and isinstance(attrObj[0], Quantity):
                    tenantDict[attr] = [e.__dict__ for e in attrObj if "__" not in e]
                elif isinstance(attrObj, User):
                    tenantDict[attr] = vars(attrObj)
                    print(tenantDict[attr])
                    attrDict = tenantDict[attr].copy()
                    for element in tenantDict[attr].keys():
                        if "__" not in element:
                            if isinstance(attrDict[element], UUID):
                                attrDict[element] = str(tenantDict[attr][element])
                        else:
                            del attrDict[element]
                    print(attrDict)
                    tenantDict[attr] = attrDict
                elif isinstance(attrObj, datetime):
                    tenantDict[attr] = attrObj.isoformat()
        return json.dumps(tenantDict)

    def from_json(attrsDict: str):
        attrsJSON = json.loads(attrsDict)
        attrsKeys = vars(Tenant)["__fields__"].keys()
        for k in attrsKeys:
            attr = attrsJSON[k]
            if k == "generalMeta":
                attrsJSON[k] = GeneralMetaData(**attr)
            if k in ["operator", "tenantUser"]:
                print(attr)
                attrsJSON[k] == User(**attr)
            if k == "quantities":
                attrsJSON[k] = [Quantity(**q) for q in attr]
            if k == "tenantServerConfig":
                attrsJSON[k] = ServerConfig(**attr)
            if k == "endRuntime":
                attrsJSON[k] = datetime.fromisoformat(attr)
        tenantObj = Tenant(**attrsJSON)
        return tenantObj

    def _get_requests(self):
        pass

    def _post_request(self):
        pass

    def _get_results(self):
        pass

    def _post_results(self):
        pass

    def run(self):
        # instantiate the FINALES server
        FINALESServer = uvicorn.Server(self.FINALESServerConfig)

        # run until the endRuntime is exceeded
        # this is intended for maintenance like refilling consumables, for which a time
        # can roughly be estimated
        while datetime.now() < self.endRuntime:
            # wait in between two requests to the server
            time.sleep(config.sleepTime_s)
            # login to the server
            print("Logging in ...")
            accessInfo = requests.post(
                f"http://{FINALESServer.config.host}:"
                "{FINALESServer.port}/userManagement/authenticate",
                data={
                    "username": tenantUser.username,
                    "password": tenantUser.password,
                    "grant_type": "password",
                },
                headers={"content-type": "application/x-www-form-urlencoded"},
            )
            print("Looking for tasks...")

            # collect the quantity names and methods in a list
            quantityNames = [q.name for q in quantities]
            quantityMethods = [q.method for q in quantities]
            # get the pending requests from the FINALES server
            pendingRequests = requests.get(
                f"http://{self.FINALESServer.config.host}"
                ":{self.FINALESServer.config.host}/???",
                params={
                    "quantityNames": quantityNames,
                    "quantityMethods": quantityMethods,
                },
                headers=accessInfo,
            ).json()
            # TODO: Which endpoint to use? What is the return value?

            for pendingItem in pendingRequests.items:
                pass


if __name__ == "__main__":
    meta = GeneralMetaData(name="testTenant", description="This is a great tenant.")

    operator = User(
        username="operator1",
        password="password1",
        usergroups=["Project_A"],
    )

    quant = Quantity(
        name="density",
        methods=["rollingBall"],
        specifications={"composition": {"a": 5, "b": 0.7}, "temperature": 273.15},
        is_active=True,
    )

    quantities = [quant]

    tenantServerConfig = ServerConfig(
        app_title="testTenant",
        app_description="A tenant for testing",
        app_version="0.0.1",
        host="0.0.0.0",
        port=1337,
    )

    FINALESServerConfig = ServerConfig(
        app_title="FINALES2",
        app_description="FINALES2 accepting requests, "
        "managing queues and serving queries",
        app_version="0.0.1",
        host="0.0.0.0",
        port=5678,
    )

    endRuntime = datetime(2023, 3, 31)

    tenantUser = User(
        username="ReferenceTenant",
        password="secretPW_forRefUsr",
        uuid=uuid4(),
        usergroups=["Project_A"],
    )

    t = Tenant(
        generalMeta=meta,
        operator=operator,
        quantities=quantities,
        tenantServerConfig=tenantServerConfig,
        FINALESServerConfig=FINALESServerConfig,
        endRuntime=endRuntime,
        tenantUser=tenantUser,
    )

    a = t.to_json()
    # b = Tenant.from_json(a)
    # print(b)
    print(Tenant.from_json(a))
