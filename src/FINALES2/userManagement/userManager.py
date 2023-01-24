import sqlite3
from fastapi import APIRouter, Depends, HTTPException
import numpy as np
from typing import Union
from uuid import uuid4
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import datetime
from jose import JWTError, jwt

try:
    from __main__ import config
except ImportError as e:
    if "pytest" in str(e):
        from FINALES2.test.filesForTests import test_config as config
    else:
        raise e

import FINALES2.userManagement.authentication as authentication
# from FINALES2.server import config
from FINALES2.schemas import User

# Create a router
userRouter = APIRouter(prefix="/userManagement", tags=["userManagement"])

# Authentication Scheme
authenticationScheme = OAuth2PasswordBearer(tokenUrl="/accessToken")
token = Depends(authenticationScheme)
cryptoContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

###################
## User Database ##
###################

class UserDB():
    ''' This class provides a database object, which allows to interface an sqlite3 database. '''

    def __init__(self, savepath:str) -> None:
        ''' This function initializes a database for storing the user data. '''
        # Print an information, which database file is used
        # Connect to this database and set the cursor
        self.connection: sqlite3.Connection = sqlite3.connect(savepath)
        self.connection.row_factory = sqlite3.Row
        self.cursor: sqlite3.Cursor = self.connection.cursor()
        self.savepath: str = savepath

        # Only create the new table, if it does not already exist
        try:
            # Deduce the column names from the fields in the User class (to allow for some flexibility in development; this could be hard-coded in a final version)
            columnNames = ", ".join(list(User.__annotations__.keys()))
            # Create a table called users with the fields of user as column names plus a timestamp for when the user was added and another for when it was last edited
            self.cursor.execute(f"create table users ({columnNames}, timestamp_added, timestamp_lastEdited)")
            print('Created new user database.')
        except sqlite3.OperationalError:
            print('Working with existing user database.')

    def addNewUser(self, user:User) -> None:
        ''' This function adds a new user with all its fields to the database. The password is hashed in this process and only the hashed value is saved to the database. '''
        # Get the dictionary of the user
        userDict = user.to_dict().copy()
        # Hash the password
        userDict['password'] = hashPassword(user.password)
        # Assemble the tuple of keys
        columnNames = tuple(list(userDict.keys()) + ["timestamp_added", "timestamp_lastEdited"])
        columnValues = tuple([str(v) for v in userDict.values()] + [str(datetime.datetime.now()), str(datetime.datetime.now())])
        # Add the data to the user database
        self.cursor.execute(f"INSERT INTO users{columnNames} VALUES {columnValues}")
        self.connection.commit()

    def userFromRow(self, row) -> User:
        rowDict = dict(row)
        return User(**rowDict)

    def getSingleUser(self, username:str, password:str) -> User:
        singleUser = self.cursor.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{hashPassword(password)}'")
        for row in singleUser:
           userdict = dict(row)
           del userdict['timestamp_added']
           del userdict['timestamp_lastEdited']
           singleU = User(**userdict)
        return singleU

    def getAllUsers(self) -> list[User]:
        allUsersCursor = self.cursor.execute("SELECT * FROM users")
        allUsers = []
        for user in allUsersCursor:
            userdict = dict(row)


        return 

    # def removeUser():
    #     ''' This function permanently deletes a user from the database. '''
    #     pass

    # def updateUser():
    #     ''' This function allows to change the fields of a user. The input values are used to overwrite the existing entries for the given user. This can e.g. be used to change passwords
    #     or user groups without creating a new user and ID. The ID of the user cannot be changed using this function. '''
    #     pass
    
    def closeConnection(self) -> None:
        ''' This function closes the connection to the database. '''
        self.connection.close()
        print("Connection to user database closed.")


def createUser(username:str, password:str, usergroups:list[str], userDB:UserDB=UserDB(config.userDB)) -> User:
    ''' This function creates a new user object and password and saves it to the database. '''
    # Instantiate a new user
    new_user = User(username=username, id=uuid4(), password=password, usergroups=usergroups)
    # Save the new user to the user database
    userDB.addNewUser(new_user)
    print(f'New user with ID {new_user.id} created and added to the user database ({userDB.savepath}).')
    return new_user

@userRouter.post("/newUser")
def newUser(username:str, password:str, usergroups:list[str]) -> None:
    createUser(userDB=UserDB(config.userDB), username=username, password=password, usergroups=usergroups)

@userRouter.get("/singleUser")
def singleUser(username:str, password:str) -> dict:
    thisUser = UserDB(config.userDB).getSingleUser(username=username, password=password)
    return thisUser.to_dict()

@userRouter.get("/allUsers")
def allUsers() -> list[dict]:
    allUsers = UserDB(config.userDB).getAllUsers()
    return allUsers

def getUserForToken(token:str=Depends(authenticationScheme)):
    return User(username="ATest", id=uuid4(), password='1111')


####################
## Authentication ##
####################
''' This implementation is based on the FastAPI documentation https://fastapi.tiangolo.com/tutorial/security/ '''

def hashPassword(password:str) -> str:
    hashedPW = cryptoContext.hash(password, salt=config.salt_userDB)
    return hashedPW

def verifyPassword(password:str, passwordHash:str) -> bool:
    return cryptoContext.verify(password, passwordHash)

@userRouter.get("/accessToken")
def getAccessToken(tokenData:dict, expirationMin:Union[datetime.timedelta, None]=None) -> str:
    tokenData = tokenData
    if expirationMin == None:
        expirationMin = datetime.timedelta(minutes=10)
    expirationTime = datetime.datetime.now() + expirationMin
    tokenData["expires"] = expirationTime
    jwtToken = jwt.encode(tokenData, config.secretKey, algorithm=config.algorithm)
    return jwtToken
    
@userRouter.post("/authenticate")
def authenticate(loginForm:OAuth2PasswordRequestForm=Depends()) -> dict[str, str]:
    userDB=UserDB(config.userDB)
    # Get the user from the user database
    thisUser = userDB.getSingleUser(username=loginForm.username, password=loginForm.password)
    # If the user is not contained in the user database, raise an error
    if thisUser==None:
        raise HTTPException(status_code=400, detail="Invalid user. Wrong username or password.")
    elif not verifyPassword(password=loginForm.password, passwordHash=thisUser.password):
        raise HTTPException(status_code=400, detail="Invalid user. Wrong username or password.")
    else:
        print("Welcome to FINALES2!")
    return {"access_token": "test", "token_type": "bearer"}

