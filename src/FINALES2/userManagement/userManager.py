import sqlite3
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Union
from uuid import uuid4
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import datetime
from jose import JWTError, jwt
from pathlib import Path


from FINALES2.server import config
import FINALES2.userManagement.authentication as authentication
from FINALES2.schemas import User, AccessToken

# Create a router
userRouter = APIRouter(prefix="/userManagement", tags=["userManagement"])

# Authentication Scheme
authenticationScheme = OAuth2PasswordBearer(tokenUrl="userManagement/authenticate")
token = Depends(authenticationScheme)
cryptoContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
authenticationError = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed. Wrong username or password.", headers={"WWW-Authenticate": "Bearer"})

###################
## User Database ##
###################

class UserDB():
    ''' This class provides a database object, which allows to interface an SQL database using sqlite3. '''

    def __init__(self, savepath:str) -> None:
        ''' This function initializes a database for storing the user data.
        
        Inputs:
        savepath: a string specifying the path, where the user database shall be stored

        Outpzt:
        This function has no output
        '''

        # Only create the new table, if it does not already exist
        if not Path(savepath).is_file():
            # Connect to this database and set the cursor
            self.connection: sqlite3.Connection = sqlite3.connect(savepath)
            self.connection.row_factory = sqlite3.Row
            self.cursor: sqlite3.Cursor = self.connection.cursor()
            self.savepath: str = savepath

            # Deduce the column names from the fields in the User class (to allow for some flexibility in development; this could be hard-coded in a final version)
            columnNames = ", ".join(User().allAttributes())
            # Create a table called users with the fields of user as column names plus a timestamp for when the user was added and another for when it was last edited
            self.cursor.execute(f"CREATE TABLE users ({columnNames}, timestamp_added, timestamp_lastEdited)")
            # Print an information, to inform about the newly created database
            print('Created new user database.')
        else:
            # Connect to this database and set the cursor
            self.connection: sqlite3.Connection = sqlite3.connect(savepath)
            self.connection.row_factory = sqlite3.Row
            self.cursor: sqlite3.Cursor = self.connection.cursor()
            self.savepath: str = savepath
            # Print an information, to inform about the use of an existing database
            print('Working with existing user database.')

    def addNewUser(self, user:User) -> None:
        ''' This function adds a new user with all its fields to the database. The password is hashed in this process and only the hashed value is saved to the database.
        
        Inputs:
        user: a user object, which shall be added to the database

        Outputs:
        This function has no output.
        '''

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

    def userFromRow(self, row:dict) -> User:
        ''' This function initializes a user object based on the input dictionary. This may be used to get a user from the result of a database query.

        Inputs:
        row: a dictionary containing at least the mandatory attributes of the User class as its keys. Additional entries in the dictionary will not be considered when creating the user object.

        Outputs:
        User: an instance of the class User with the attributes set according to the entries in the row parameter
        '''

        return User(**row)

    def getSingleUser(self, username:str) -> User:
        ''' This function finds a user in the user database by its username. It raises an error, if there are several users with the same username.

        Inputs:
        username: a string specifying the username to look for

        Outputs:
        singleU: an instance of the User class with the attributes set according to the entries in the user database corresponding to this username        
        '''

        # Query all the users for this username from the user database
        singleUser = self.cursor.execute(f"SELECT * FROM users WHERE username=?", (username))
        row = singleUser.fetchall()
        # If there is only one user with this username
        if len(row) == 1:
            # Create a user from the result of the query and return it
            singleU = self.userFromRow(row[0])
            return singleU
        else:
            # If there are more than one or no user with this username, raise an exception
            HTTPException(status_code=403, detail="More than one user with this username was found.")

    def getAllUsers(self) -> list[User]:
        ''' This fuction requests all the users in the user database and returns them as a list of user objects.

        Inputs:
        This function takes no inputs.

        Outputs:
        allUsers: a list of objects of the class User, each having its attributes set according to the corresponding row in the user database.
        '''

        # Query the user database for all its entries
        allUsersCursor = self.cursor.execute("SELECT * FROM users")
        # Initialize the empty list to collect all the user objects
        allUsers = []
        # Iterate over all the users found in the user database
        for user in allUsersCursor.fetchall():
            # Get the user object for the respective row
            oneUser = self.userFromRow(user)
            # Append the user to the list of all users
            allUsers.append(oneUser)
        # Return the list of users
        return allUsers

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

def createUser(username:str, password:str, usergroups:list[str], userDB:str=config.userDB) -> User:
    ''' This function creates a new user object and password and saves it to the database. '''
    userDB = UserDB(userDB)
    # Instantiate a new user
    new_user = User(username=username, password=password, usergroups=usergroups)
    # Save the new user to the user database
    userDB.addNewUser(new_user)
    print(f'New user with ID {new_user.id} created and added to the user database ({userDB.savepath}).')
    return new_user

@userRouter.post("/newUser")
def newUser(username:str, password:str, usergroups:list[str], userDB:str=config.userDB) -> None:
    createUser(userDB=userDB, username=username, password=password, usergroups=usergroups)
    return f"New user {username} created in user database {userDB}."

@userRouter.get("/singleUser")
def singleUser(username:str) -> dict:
    thisUser = UserDB(config.userDB).getSingleUser(username=username)
    thisUser = thisUser.to_dict()
    return thisUser

@userRouter.get("/allUsers")
def allUsers() -> list[dict]:
    allUsers = UserDB(config.userDB).getAllUsers()
    allUsers = [user.to_dict() for user in allUsers]
    return allUsers

def getUserForToken(token:str=Depends(authenticationScheme)) -> User:
    return User(username="ATest", id=uuid4(), password='1111')

def getActiveUser(token:str=Depends(authenticationScheme)) -> User:
    try:
        decodedJWT = jwt.decode(token, config.secretKey, algorithms=[config.algorithm])
        activeUsername:str = decodedJWT.get("sub")
        if activeUsername is None:
            raise authenticationError
    except JWTError:
        raise authenticationError
    activeUser = singleUser(username=activeUsername)
    return activeUser

####################
## Authentication ##
####################
''' This implementation is based on the FastAPI documentation https://fastapi.tiangolo.com/tutorial/security/ '''

def hashPassword(password:str) -> str:
    hashedPW = cryptoContext.hash(password, salt=config.salt_userDB)
    return hashedPW

def verifyPassword(password:str, passwordHash:str) -> bool:
    return cryptoContext.verify(password, passwordHash)

def getAccessToken(tokenData:dict, expirationMin:Union[datetime.timedelta, None]=None) -> str:
    tokenData = tokenData.copy()
    if expirationMin == None:
        expirationMin = datetime.timedelta(minutes=10)
    expirationTime = datetime.datetime.now() + expirationMin
    tokenData["exp"] = expirationTime
    jwtToken = jwt.encode(tokenData, config.secretKey, algorithm=config.algorithm)
    return jwtToken

def userAuthentication(username:str, password:str):
    user = User(**singleUser(username=username))
    if verifyPassword(password=password, passwordHash=user.password):
        return user
    else:
        raise authenticationError

@userRouter.post("/authenticate")
def authenticate(loginForm:OAuth2PasswordRequestForm=Depends()) -> dict[str, str]:
    userDB=UserDB(config.userDB)
    # Get the user from the user database and check, if the password is correct
    thisUser = userAuthentication(username=loginForm.username, password=loginForm.password)
    tokenExpiration = datetime.timedelta(minutes=config.tokenExpirationMin)
    accessToken = getAccessToken(tokenData={"sub": thisUser.username}, expirationMin=tokenExpiration)
    print("Welcome to FINALES2!")
    return {"access_token": accessToken, "token_type": "bearer"}

# uDB = UserDB(r'C:\Users\MonikaVogler\Documents\BIG-MAP\FINALES2\FINALES2\src\FINALES2\userManagement\userDB.db')
# uDB.addNewUser(User())
# uDB.getAllUsers()