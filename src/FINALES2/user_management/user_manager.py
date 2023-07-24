import datetime
import sqlite3
from typing import Any, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from FINALES2.config import get_configuration
from FINALES2.user_management.classes_user_manager import AccessToken, User

# Create a router
user_router = APIRouter(prefix="/user_management", tags=["user_management"])

# Authentication Scheme
authentication_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{user_router.prefix.strip('/')}/authenticate"
)
token = Depends(authentication_scheme)
crypto_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
authentication_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authentication failed. Wrong username or password.",
    headers={"WWW-Authenticate": "Bearer"},
)


# User Database


class UserDB:
    """This class provides a database object, which allows to interface an SQL user
    database using sqlite3."""

    def __init__(self, savepath: Optional[str] = None) -> None:
        """This function initializes a database for storing the user data.

        Inputs:
        savepath: a string specifying the path, where the user database shall be stored

        Output:
        This function has no output
        """
        if savepath is None:
            config = get_configuration()
            savepath = config.safeget_userdb()

        # Connect to this database and set the cursor
        self.connection: sqlite3.Connection = sqlite3.connect(savepath)
        self.connection.row_factory = sqlite3.Row
        self.cursor: sqlite3.Cursor = self.connection.cursor()
        self.savepath: str = savepath

        # Only create the new table, if it does not already exist

        # Deduce the column names from the fields in the User class (to allow for
        # some flexibility in development; this could be hard-coded in a final
        # version)
        column_names = ", ".join(User().__dict__.keys())
        # Create a table called users with the fields of user as column names
        # plus a timestamp for when the user was added and another for when it
        # was last edited
        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS users ({column_names}, timestamp_added"
            ", timestamp_lastEdited)"
        )

    def close_connection(self) -> None:
        """This function closes the connection to the user database.

        Inputs:
        This function takes no inputs.

        Outputs:
        This function has no output.
        """

        # Close the connection to the user database
        self.connection.close()

    def connect(self) -> None:
        """This function connects to an existing instance of a database.

        Inputs:
        This function takes no inputs.

        Outputs:
        This function has no output.
        """

        self.connection = sqlite3.connect(self.savepath)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def add_new_user(self, user: User) -> None:
        """This function adds a new user with all its fields to the database.
        The password is hashed in this process and only the hashed value is saved
        to the database.

        Inputs:
        user: a user object, which shall be added to the database

        Outputs:
        This function has no output.
        """

        self.connect()

        # Get the dictionary of the user
        user_dict = user.__dict__.copy()
        # Hash the password
        user_dict["password"] = hash_password(user.password)
        # Assemble the tuple of keys
        column_names = tuple(
            list(user_dict.keys()) + ["timestamp_added", "timestamp_lastEdited"]
        )
        column_values = tuple(
            [str(v) for v in user_dict.values()]
            + [str(datetime.datetime.now()), str(datetime.datetime.now())]
        )
        # Add the data to the user database
        self.cursor.execute(f"INSERT INTO users{column_names} VALUES {column_values}")
        self.connection.commit()
        self.close_connection()

    def user_from_row(self, row: dict) -> User:
        """This function initializes a user object based on the input dictionary.
        This may be used to get a user from the result of a database query.

        Inputs:
        row: a dictionary containing at least the mandatory attributes of the User
             class as its keys. Additional entries in the dictionary will not be
             considered when creating the user object.

        Outputs:
        User: an instance of the class User with the attributes set according to the
              entries in the row parameter
        """

        row_update = {}
        for key in row.keys():
            if key == "usergroups":
                row_update["usergroups"] = eval(row["usergroups"])
            else:
                row_update[key] = row[key]

        return User(**row_update)

    def get_single_user(self, username: str) -> User:
        """This function finds a user in the user database by its username. It raises
        an error, if there are several users with the same username.

        Inputs:
        username: a string specifying the username to look for

        Outputs:
        single_u: an instance of the User class with the attributes set according to the
                 entries in the user database corresponding to this username
        """

        self.connect()

        # Query all the users for this username from the user database
        single_user = self.cursor.execute(
            "SELECT * FROM users WHERE username=(?)", (username,)
        )
        row = single_user.fetchall()
        # If there is only one user with this username
        if len(row) == 1:
            # Create a user from the result of the query and return it
            single_u = self.user_from_row(row[0])
            self.close_connection()
            return single_u
        elif len(row) > 1:
            # If there are more than one user with this username,
            # raise an exception
            self.close_connection()
            raise HTTPException(
                status_code=409,
                detail="More than one user with this username was found.",
            )
        else:
            # If there is no user with this username,
            # raise an exception
            self.close_connection()
            raise HTTPException(
                status_code=404,
                detail="No user with this username was found.",
            )

    def get_all_users(self) -> list[User]:
        """This fuction requests all the users in the user database and returns them as
        a list of user objects.

        Inputs:
        This function takes no inputs.

        Outputs:
        all_users: a list of objects of the class User, each having its attributes set
                  according to the corresponding row in the user database.
        """

        self.connect()

        # Query the user database for all its entries
        all_users_cursor = self.cursor.execute("SELECT * FROM users")
        # Initialize the empty list to collect all the user objects
        all_users = []
        # Iterate over all the users found in the user database
        for user in all_users_cursor.fetchall():
            # Get the user object for the respective row
            one_user = self.user_from_row(user)
            # Append the user to the list of all users
            all_users.append(one_user)
        self.close_connection
        # Return the list of users
        return all_users

    # def removeUser():
    #     ''' This function permanently deletes a user from the database. '''
    #     pass

    # # def updateUser():
    #     ''' This function allows to change the fields of a user. The input values are
    #     used to overwrite the existing entries for the given user. This can e.g. be
    #     used to change passwords or user groups without creating a new user and ID.
    #     The ID of the user cannot be changed using this function. '''
    #     pass


def create_user(username: str, password: str, usergroups: list[str]) -> User:
    """This function creates a new user object connected to the given password and saves
    it to the database.

    Inputs:
    username: a string specifying the username
    password: a string representing the plain text password
    usergroups: a list of strings providing all the user groups, to which the user is
                assigned

    Outputs:
    new_user: a user object with all the data set as in the user database
    """

    # Instantiate the user database
    user_db = UserDB()
    # To check, if a user is obtained from the database
    user_in_db = None

    # Instantiate a new user
    new_user = User(username=username, password=password, usergroups=usergroups)
    # Save the new user to the user database, if it not already exists
    try:
        user_in_db = user_db.get_single_user(username=new_user.username)
    except HTTPException as e:
        if e.status_code == 404:
            user_db.add_new_user(new_user)
            # Get the just added user from the user database and return it.
            new_user = user_db.get_single_user(username=new_user.username)
        else:
            raise ValueError(
                "This username cannot be added to the database. "
                "Pleas contact the user administrator."
            )
    if not (user_in_db is None):
        raise ValueError(
            "This username cannot be added to the database. "
            "Please choose a different one and try again."
        )
    return new_user


# @user_router.post("/new_user")
def new_user(username: str, password: str, usergroups: list[str]) -> str:
    """This function creates a new user in a user database.

    Inputs:
    username: a string defining the username of the user
    password: a string specifying the plain text password for the user
    usergroups: a list of strings representing the usergroups, of which the user is a
                member

    Outputs:
    An information for the user is printed.
    """
    # Create the new user in the database and print a message to the operator about the
    # newly created user.
    new_user = create_user(username=username, password=password, usergroups=usergroups)
    return f"New user {new_user.username} created in user database."


# @user_router.get("/single_user")
def single_user(username: str) -> dict[str, Any]:
    """This function fetches a single user from the user database based on its username
    and returns the corresponding dictionary of the user object.

    Inputs:
    username: a string specifying the username of the user

    Outputs:
    this_user: a dictionary created based on the attributes of the user object collected
              from the user database
    """

    # Connect to the user database
    user_db = UserDB()
    # Get the user from the user database
    this_user = user_db.get_single_user(username=username)
    # Transform the user object to a dictionary and return it
    this_user_dict = this_user.__dict__
    return this_user_dict


# @user_router.get("/all_users")
def all_users() -> list[dict]:
    """This function collects all the users saved in the user database.

    Inputs:
    This function takes no inputs.

    Outputs:
    all_users: a list of dictionaries comprising a dictionary for each user collected
              from the user database
    """

    # Get all the entries from the user database
    all_users = UserDB().get_all_users()
    # Collect the dictionaries of all the users in a list and return the list
    all_users_dict = [user.__dict__ for user in all_users]
    return all_users_dict


def get_active_user(token: str = Depends(authentication_scheme)) -> dict[str, Any]:
    """This function returns the user, to which the given token belongs, if the token
    belongs to a user.

    Inputs:
    token: a string used to extract the username from to search for the user in the
           user database

    Outputs:
    active_user: a user object created based on a query to the user database with the
                username obtained from the token
    """
    config = get_configuration()
    # Try to decode the token
    try:
        decoded_JWT = jwt.decode(
            token, config.secret_key, algorithms=[config.algorithm]
        )
        # Get the username from the token
        active_username: str = decoded_JWT.get("sub")
        # If there is no username, raise an authentication exception
        if active_username is None:
            raise authentication_error
    # If the decoding fails, raise an authentication exception
    except JWTError:
        raise authentication_error
    # If there is a username, find the corresponding user in the user database and
    # return it
    active_user = single_user(username=active_username)
    return active_user


# Authentication

""" This implementation is based on the FastAPI documentation
https://fastapi.tiangolo.com/tutorial/security/ """


def hash_password(password: str) -> str:
    """This function hashes a plain text password.

    Inputs:
    password: a string representing the plain text password of a user

    Outputs:
    hashPW: a string representing the hash of the plain text password
    """

    # Hash the password and return it
    hashed_PW = crypto_context.hash(password)
    return hashed_PW


def verify_password(
    password: str, password_hash: str
) -> bool:  # Corresponds to verify_passwprd of the tutorial
    """This function verifies a password.

    Inputs:
    password: a string representing the plain text password
    password_hash: a string representing the hash, which should match the password

    Outputs:
    verification: a boolean, which is True, if the password matches the hash, and
                  False otherwise
    """

    verification = crypto_context.verify(password, password_hash)
    return verification


def get_access_token(
    token_data: dict, expiration_min: Union[datetime.timedelta, None] = None
) -> str:
    """This function generates an access token for a user.

    Inputs:
    token_data: a dictionary containing the information needed to create the token
    expiration_min: a timedelta giving the duration until the expiration of the token
                   in minutes or None

    Outputs:
    token_JWT: a string representing the token generated
    """
    config = get_configuration()

    # Create a copy of the token data
    token_data = token_data.copy()
    # If no expiration time is given, use 10 min
    if expiration_min is None:
        expiration_min = datetime.timedelta(minutes=10)

    # Add the expiration duration to now
    expiration_time = datetime.datetime.now() + expiration_min
    # Save the expiration time to the token_data using the key "exp" (it needs to be
    # called exp, because there will be a TypeError otherwise)
    token_data["exp"] = expiration_time
    # Encode the token and return it
    token_JWT = jwt.encode(token_data, config.secret_key, algorithm=config.algorithm)
    return token_JWT


def user_authentication(username: str, password: str) -> User:
    """This function authenticates a user.

    Inputs:
    username: a string giving the username of the user, which needs authentication
    password: a string of the plain text password of the user, which needs
              authentication

    Outputs:
    user: a user object matching the requested username and password. If the password
          is not correct, an authentication exception is raised
    """

    # Get the user from the user database based on its username
    user_dict = single_user(username=username)
    # Create the user object from the output
    user = User(**user_dict)
    # Verify the password and return it, if it is correct
    if verify_password(password=password, password_hash=user.password):
        return user
    # Raise an authenticatin exception otherwise
    else:
        raise authentication_error


@user_router.post("/authenticate", response_model=AccessToken)
def authenticate(login_form: OAuth2PasswordRequestForm = Depends()) -> dict[str, str]:
    """The function allows a user to log in.

    Inputs:
    login_form: a login form comprising the username and the password to use for the
                login

    Outputs:
    tokenInfo: a dictionary with the relevant AccessToken and token_type
    """
    config = get_configuration()

    # Get the user from the user database and check, if the password is correct
    this_user = user_authentication(
        username=login_form.username, password=login_form.password
    )
    # Define the expiration time
    token_expiration = datetime.timedelta(minutes=config.token_expiration_min)
    # Get the access token for the user
    access_token = get_access_token(
        token_data={"sub": this_user.username}, expiration_min=token_expiration
    )
    # Print an information to the user
    print(f"Welcome to FINALES2! You are logged in as {login_form.username}.")
    # Assemble and return the access information
    access_info = {"access_token": access_token, "token_type": "bearer"}
    return access_info
