import uvicorn
from fastapi import Depends, FastAPI

from FINALES2.schemas import User
from FINALES2.server import config
from FINALES2.userManagement import userManager

app = FastAPI(
    title="FINALES2",
    description="FINALES2 accepting requests, managing queues and serving queries",
    version="0.0.1",
)

app.include_router(router=userManager.userRouter)


@app.get("/")
def Hello():
    return "Hello! This is FINALES2."


@app.get("/test")
def test(token: User = Depends(userManager.getActiveUser)):
    print(config.userDB)
    return token


if __name__ == "__main__":
    uvicorn.run(app=app, host=config.host, port=config.port)
