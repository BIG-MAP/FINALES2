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
from FINALES2.schemas import AccessToken, User

# Create a router
userRouter = APIRouter(prefix="/userManagement", tags=["userManagement"])

# Authentication Scheme
authenticationScheme = OAuth2PasswordBearer(
    tokenUrl=f"{userRouter.prefix.strip('/')}/authenticate"
)
token = Depends(authenticationScheme)
cryptoContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
authenticationError = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authentication failed. Wrong username or password.",
    headers={"WWW-Authenticate": "Bearer"},
)

###################
## User Database ##
###################


class UserDB:
    """This class provides a database object, which allows to interface an SQL user database using sqlite3."""

    def __init__(self, savepath: str) -> None:
        """This function initializes a database for storing the user data.

        Inputs:
        savepath: a string specifying the path, where the user database shall be stored

        Outpzt:
        This function has no output
        """

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
            self.cursor.execute(
                f"CREATE TABLE users ({columnNames}, timestamp_added, timestamp_lastEdited)"
            )
            # Print an information, to inform about the newly created database
            print("Created new user database.")
        else:
            # Connect to this database and set the cursor
            self.connection: sqlite3.Connection = sqlite3.connect(savepath)
            self.connection.row_factory = sqlite3.Row
            self.cursor: sqlite3.Cursor = self.connection.cursor()
            self.savepath: str = savepath
            # Print an information, to inform about the use of an existing database
            print("Working with existing user database.")

    def closeConnection(self) -> None:
        """This function closes the connection to the user database.

        Inputs:
        This function takes no inputs.

        Outputs:
        This function has no output.
        """

        # Close the connection to the user database
        self.connection.close()
        # Print an information to the user
        print("Connection to user database closed.")

    def addNewUser(self, user: User) -> None:
        """This function adds a new user with all its fields to the database. The password is hashed in this process and only the hashed value is saved to the database.

        Inputs:
        user: a user object, which shall be added to the database

        Outputs:
        This function has no output.
        """

        # Get the dictionary of the user
        userDict = user.to_dict().copy()
        # Hash the password
        userDict["password"] = hashPassword(user.password)
        # Assemble the tuple of keys
        columnNames = tuple(
            list(userDict.keys()) + ["timestamp_added", "timestamp_lastEdited"]
        )
        columnValues = tuple(
            [str(v) for v in userDict.values()]
            + [str(datetime.datetime.now()), str(datetime.datetime.now())]
        )
        # Add the data to the user database
        self.cursor.execute(f"INSERT INTO users{columnNames} VALUES {columnValues}")
        self.connection.commit()

    def userFromRow(self, row: dict) -> User:
        """This function initializes a user object based on the input dictionary. This may be used to get a user from the result of a database query.

        Inputs:
        row: a dictionary containing at least the mandatory attributes of the User class as its keys. Additional entries in the dictionary will not be considered when creating the user object.

        Outputs:
        User: an instance of the class User with the attributes set according to the entries in the row parameter
        """

        return User(**row)

    def getSingleUser(self, username: str) -> User:
        """This function finds a user in the user database by its username. It raises an error, if there are several users with the same username.

        Inputs:
        username: a string specifying the username to look for

        Outputs:
        singleU: an instance of the User class with the attributes set according to the entries in the user database corresponding to this username
        """

        # Query all the users for this username from the user database
        singleUser = self.cursor.execute(
            f"SELECT * FROM users WHERE username=(?)", (username,)
        )
        row = singleUser.fetchall()
        # If there is only one user with this username
        if len(row) == 1:
            # Create a user from the result of the query and return it
            singleU = self.userFromRow(row[0])
            return singleU
        else:
            # If there are more than one or no user with this username, raise an exception
            raise HTTPException(
                status_code=403,
                detail="More than one user with this username was found.",
            )

    def getAllUsers(self) -> list[User]:
        """This fuction requests all the users in the user database and returns them as a list of user objects.

        Inputs:
        This function takes no inputs.

        Outputs:
        allUsers: a list of objects of the class User, each having its attributes set according to the corresponding row in the user database.
        """

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


def createUser(
    username: str, password: str, usergroups: list[str], userDB: str = config.userDB
) -> User:
    """This function creates a new user object connected to the given password and saves it to the database.

    Inputs:
    username: a string specifying the username
    password: a string representing the plain text password
    usergroups: a list of strings providing all the user groups, to which the user is assigned
    userDB: a string giving the path, where the user database is stored

    Outputs:
    new_user: a user object with all the data set as in the user database
    """

    # Instantiate the user database
    userDB = UserDB(userDB)
    # Instantiate a new user
    new_user = User(username=username, password=password, usergroups=usergroups)
    # Save the new user to the user database
    userDB.addNewUser(new_user)
    # Print an information to the operator
    print(
        f"New user with ID {new_user.id} created and added to the user database ({userDB.savepath})."
    )
    # Get the just added user from the user database and return it.
    new_user = userDB.getSingleUser(username=new_user.username)
    userDB.closeConnection()
    return new_user


@userRouter.post("/newUser")
def newUser(
    username: str, password: str, usergroups: list[str], userDB: str = config.userDB
) -> None:
    """This function creates a new user in a user database.

    Inputs:
    username: a string defining the username of the user
    password: a string specifying the plain text password for the user
    usergroups: a list of strings representing the usergroups, of which the user is a member
    userDB: a string specifying the path to the user database

    Outputs:
    This function has no output.
    """

    # Create the new user in the database and print a message to the operator about the newly created user.
    createUser(
        userDB=userDB, username=username, password=password, usergroups=usergroups
    )
    return f"New user {username} created in user database {userDB}."


@userRouter.get("/singleUser")
def singleUser(username: str, userDB: str = config.userDB) -> dict:
    """This function fetches a single user from the user database based on its username and returns the corresponding dictionary of the user object.

    Inputs:
    username: a string specifying the username of the user

    Outputs:
    thisUser: a dictionary created based on the attributes of the user object collected from the user database
    """

    # Get the user from the user database
    thisUser = UserDB(userDB).getSingleUser(username=username)
    # Transform the user object to a dictionary and return it
    thisUser = thisUser.to_dict()
    return thisUser


@userRouter.get("/allUsers")
def allUsers(userDB: str = config.userDB) -> list[dict]:
    """This function collects all the users saved in the user database.

    Inputs:
    userDB: a string specifying the path to the user database, which shall be queried

    Outputs:
    allUsers: a list of dictionaries comprising a dictionary for each user collected from the user database
    """

    # Get all the entries from the user database
    allUsers = UserDB(userDB).getAllUsers()
    # Collect the dictionaries of all the users in a list and return the list
    allUsers = [user.to_dict() for user in allUsers]
    return allUsers


def getActiveUser(
    token: str = Depends(authenticationScheme), userDB: str = config.userDB
) -> User:
    """This function returns the user, to which the given token belongs, if the token belongs to a user.

    Inputs:
    token: a string used to extract the username from to search for the user in the user database

    Outputs:
    activeUser: a user object created based on a query to the user database with the username obtained from the token
    """

    # Try to decode the token
    try:
        decodedJWT = jwt.decode(token, config.secretKey, algorithms=[config.algorithm])
        # Get the username from the token
        activeUsername: str = decodedJWT.get("sub")
        # If there is no username, raise an authentication exception
        if activeUsername is None:
            raise authenticationError
    # If the decoding fails, raise an authentication exception
    except JWTError:
        raise authenticationError
    # If there is a username, find the corresponding user in the user database and return it
    activeUser = singleUser(username=activeUsername, userDB=userDB)
    return activeUser


####################
## Authentication ##
####################
""" This implementation is based on the FastAPI documentation https://fastapi.tiangolo.com/tutorial/security/ """


def hashPassword(password: str) -> str:
    """This function hashes a plain text password.

    Inputs:
    password: a string representing the plain text password of a user

    Outputs:
    hashPW: a string representing the hash of the plain text password
    """

    # Hash the password and return it
    hashedPW = cryptoContext.hash(password)
    return hashedPW


def verifyPassword(
    password: str, passwordHash: str
) -> bool:  # Corresponds to verify_passwprd of the tutorial
    """This function verifies a password.

    Inputs:
    password: a string representing the plain text password
    passwordHash: a string representing the hash, which should match the password

    Outputs:
    verification: a boolean, which is True, if the password matches the hash, and False otherwise
    """

    verification = cryptoContext.verify(password, passwordHash)
    return verification


def getAccessToken(
    tokenData: dict, expirationMin: Union[datetime.timedelta, None] = None
) -> str:
    """This function generates an access token for a user.

    Inputs:
    tokenData: a dictionary containing the information needed to create the token
    expirationMin: a timedelta giving the duration until the expiration of the token in minutes or None

    Outputs:
    jwtToken: a string representing the token generated
    """

    # Create a copy of the token data
    tokenData = tokenData.copy()
    # If no expiration time is given, use 10 min
    if expirationMin == None:
        expirationMin = datetime.timedelta(minutes=10)

    # Add the expiration duration to now
    expirationTime = datetime.datetime.now() + expirationMin
    # Save the expiration time to the tokenData using the key "exp" (it needs to be called exp, because there will be a TypeError otherwise)
    tokenData["exp"] = expirationTime
    # Encode the token and return it
    jwtToken = jwt.encode(tokenData, config.secretKey, algorithm=config.algorithm)
    return jwtToken


def userAuthentication(
    username: str, password: str, userDB: str = config.userDB
) -> User:
    """This function authenticates a user.

    Inputs:
    username: a string giving the username of the user, which needs authentication
    password: a string of the plain text password of the user, which needs authentication

    Outputs:
    user: a user object matching the requested username and password. If the password is not correct, an authentication exception is raised
    """

    # Get the user from the user database based on its username
    userDict = singleUser(username=username, userDB=userDB)
    # Create the user object from the output
    user = User(**userDict)
    # Verify the password and return it, if it is correct
    if verifyPassword(password=password, passwordHash=user.password):
        return user
    # Raise an authenticatin exception otherwise
    else:
        raise authenticationError


@userRouter.post("/authenticate", response_model=AccessToken)
def authenticate(
    loginForm: OAuth2PasswordRequestForm = Depends(), userDB: str = config.userDB
) -> dict[str, str]:
    """The function allows a user to log in.

    Inputs:
    loginForm: a loginForm comprising the username and the password to use for the login

    Outputs:
    tokenInfo: a dictionary with the relevant access_token and token_type
    """

    # Get the user from the user database and check, if the password is correct
    thisUser = userAuthentication(
        username=loginForm.username, password=loginForm.password, userDB=userDB
    )
    # Define the expiration time
    tokenExpiration = datetime.timedelta(minutes=config.tokenExpirationMin)
    # Get the access token for the user
    accessToken = getAccessToken(
        tokenData={"sub": thisUser.username}, expirationMin=tokenExpiration
    )
    # Print an information to the user
    print("Welcome to FINALES2!")
    # Assemble and return the access information
    accessInfo = {"access_token": accessToken, "token_type": "bearer"}
    return accessInfo
