import time
from datetime import datetime
from typing import Optional
from uuid import uuid4

# import jsons
import requests
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

import FINALES2.server.config as config
from FINALES2.schemas import GeneralMetaData, Quantity, User


class tenant(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    generalMeta: GeneralMetaData
    operator: User
    quantities: list[Quantity]
    tenantServerConfig: uvicorn.Config
    FINALESServerConfig: uvicorn.Config
    endRuntime: Optional[datetime]
    tenantUser: User

    def serialize(self):
        pass
        # tenantSerialized = jsons.dump(
        #     self,
        #     key_transformer=jsons.KEY_TRANSFORMER_PASCALCASE
        #     )
        # return tenantSerialized

    def deserialize(self):
        pass

    def _get_requests(self):
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
    meta = GeneralMetaData(
        name="testTenant", uuid=uuid4(), description="This is a great tenant."
    )

    operator = User(
        username="operator1",
        password="password1",
        uuid=uuid4(),
        usergroups=["Project_A"],
    )

    quant = Quantity(
        name="density",
        method=["rollingBall"],
        specifications={"composition": {"a": 5, "b": 0.7}, "temperature": 273.15},
        is_active=True,
        uuid=uuid4(),
        load_time=datetime.now(),
    )

    quantities = [quant]

    tenantServerConfig = uvicorn.Config(
        app=FastAPI(
            title="testTenant", description="A tenant for testing", version="0.0.1"
        ),
        host="0.0.0.0",
        port=1337,
    )

    FINALESServerConfig = uvicorn.Config(
        app=FastAPI(
            title="FINALES2",
            description="FINALES2 accepting requests, "
            "managing queues and serving queries",
            version="0.0.1",
        ),
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

    t = tenant(
        generalMeta=meta,
        operator=operator,
        quantities=quantities,
        tenantServerConfig=tenantServerConfig,
        FINALESServerConfig=FINALESServerConfig,
        endRuntime=endRuntime,
        tenantUser=tenantUser,
    )

    ts = t.serialize()
    print(type(ts), ts)
