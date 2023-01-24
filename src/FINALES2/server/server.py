
from typing import List
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
import requests
from uuid import uuid4

from FINALES2.server import config
from FINALES2.schemas import User
from FINALES2.userManagement import userManager

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI(title="FINALES2",
              description="FINALES2 accepting requests, managing queues and serving queries",
              version="0.0.1")

app.include_router(router=userManager.userRouter)

@app.get("/test")
def test(token:User=Depends(userManager.getUserForToken)):
    return token

# @app.post("/authenticate")
# async def userAuthentication(data:OAuth2PasswordRequestForm=Depends()):
#     accessData = userManager.authenticate(data)
#     return accessData

uvicorn.run(app=app, host=config.host, port=config.port)