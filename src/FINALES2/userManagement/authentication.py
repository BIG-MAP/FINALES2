# ''' This file provides the functionalities to authenticate a user on the FINALES server. In the future, it will also provide the functionalities to group users and administer the user groups. '''

# #############
# ## Imports ##
# #############

# import typing
# from fastapi import APIRouter, FastAPI, Depends, HTTPException
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from passlib.context import CryptContext
# import datetime
# from jose import JWTError, jwt
# import requests



# from FINALES2 import schemas
# from FINALES2.server import config
# import FINALES2.userManagement.userManager as userManager

# # Create the router
# authorizationRouter = APIRouter(prefix="/authorization", tags=['authorization'])


