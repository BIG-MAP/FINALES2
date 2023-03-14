import datetime
from glob import glob
from os import remove
from sqlite3 import ProgrammingError
from uuid import UUID

from jose import jwt
from passlib.context import CryptContext
from pytest import raises

from FINALES2.schemas import User
from FINALES2.test.filesForTests import test_config
from FINALES2.userManagement import userManager


def test_UserDB_init():
    # Get the path to the folder, where the user database is stored from the config file
    filepath = "/".join(test_config.userDB.split("/")[0:-1])
    print(filepath)

    # Delete potentially existing user databases
    for file in glob(f"{filepath}/*.db"):
        remove(file)

    # Test Case 1: New user database

    # Create the user database
    db = userManager.UserDB(test_config.userDB)

    # Get the target list of column names
    columns_target = list(User.__annotations__.keys()) + [
        "timestamp_added",
        "timestamp_lastEdited",
    ]

    # Get the resulting list of column names
    allColumns = db.cursor.execute("SELECT * FROM users")
    columns_result = [element[0] for element in allColumns.description]

    # Check that all target column names are in the result column names
    for col in columns_target:
        assert col in columns_result, (
            f"The target column name {col} is not in the resulting column names for "
            f"the new database."
        )

    # Close the connection to the database
    db.closeConnection()

    # Test Case 2: Work with existing database

    # Reconnect to the existing database
    db = userManager.UserDB(test_config.userDB)

    # Get the resulting list of column names
    allColumns = db.cursor.execute("SELECT * FROM users")
    columns_result = [element[0] for element in allColumns.description]

    # Check that all target column names are in the result column names
    for col in columns_target:
        assert col in columns_result, (
            f"The target column name {col} is not in the resulting column names for "
            "the existing user database."
        )

    # Close the connection to the database
    db.closeConnection()


def test_UserDB_closeConnection():
    # Connect to the user database or create a new one
    db = userManager.UserDB(test_config.userDB)
    db.closeConnection()

    with raises(ProgrammingError):
        db.cursor.execute("SELECT * FROM users")


def test_UserDB_addNewUser():
    db = userManager.UserDB(test_config.userDB)
    user = User(
        username="testUser",
        id=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-",
        usergroups=["1", "2", "3"],
    )
    print(user.__dict__)
    db.addNewUser(user)

    data_result = db.cursor.execute("SELECT * FROM users").fetchone()
    data_target = tuple(list(str(v) for v in user.to_dict().values()))

    for i in range(4):
        if i != 2:
            data_result[i] == data_target[
                i
            ], f"The found data is {data_result[i]} instead of {data_target[i]}."
        else:
            data_result[i] == userManager.hashPassword(data_target[i]), (
                f"The found data is {userManager.hashPassword(data_result[i])} "
                f"instead of {data_target[i]}."
            )
    # TODO: check the timestamps#, '2023-01-14 17:06:17.416907'
    # , '2023-01-14 17:06:17.416907')]
    db.closeConnection()


def test_UserDB_userFromRow():
    db = userManager.UserDB(test_config.userDB)
    referenceUser = User(
        username="testUser2",
        id=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-2",
        usergroups=["1", "2", "3"],
    )
    db.addNewUser(referenceUser)

    aUser = db.cursor.execute(
        "SELECT * FROM users WHERE username=(?)", (referenceUser.username,)
    )
    row = aUser.fetchall()

    theUser = db.userFromRow(row[0])

    assert isinstance(theUser, User), (
        f"The object obtained from the userFromRow method is of "
        f"type {type(theUser)}instead of User."
    )

    for key in row[0].keys():
        if ("password" not in key) and ("timestamp" not in key):
            assert getattr(theUser, key) == row[0][key], (
                f"The {key} of the object differs from the row. It is "
                f"{getattr(theUser, key)} instead of {row[0][key]}."
            )

    db.closeConnection()


def test_UserDB_getSingleUser():
    db = userManager.UserDB(test_config.userDB)
    referenceUser = User(
        username="testUser3",
        id=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-3",
        usergroups=["1", "2", "3"],
    )
    db.addNewUser(referenceUser)

    user_result = db.getSingleUser(username=referenceUser.username)

    db.closeConnection()

    for attr in referenceUser.allAttributes():
        if attr == "password":
            assert userManager.verifyPassword(
                password=referenceUser.__getattribute__(attr),
                passwordHash=user_result.__getattribute__(attr),
            )
        else:
            assert str(
                referenceUser.__getattribute__(attr)
            ) == user_result.__getattribute__(attr)


def test_UserDB_getAllUsers():
    db = userManager.UserDB(test_config.userDB)
    allUsers_result = db.getAllUsers()
    allUsers_reference = [
        User(
            username="testUser",
            id=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-",
            usergroups=["1", "2", "3"],
        ),
        User(
            username="testUser2",
            id=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-2",
            usergroups=["1", "2", "3"],
        ),
        User(
            username="testUser3",
            id=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-3",
            usergroups=["1", "2", "3"],
        ),
    ]

    assert all(
        [isinstance(u, User) for u in allUsers_result]
    ), "Not all objects in the obtained list of all users are of type User"

    for user in allUsers_reference:
        assert (
            user in allUsers_result
        ), f"The user {user.username} is not contained in the obtained all users."


def test_createUser():
    referenceUser2 = User(
        username="testUser4",
        id=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-4",
        usergroups=["1", "2", "3"],
    )

    user_result2 = userManager.createUser(
        username=referenceUser2.username,
        password=referenceUser2.password,
        usergroups=referenceUser2.usergroups,
        userDB=test_config.userDB,
    )

    for attr in referenceUser2.allAttributes():
        if attr == "password":
            assert userManager.verifyPassword(
                password=referenceUser2.__getattribute__(attr),
                passwordHash=user_result2.__getattribute__(attr),
            ), "The password of the user does not match the target."
        elif attr != "id":
            assert str(
                referenceUser2.__getattribute__(attr)
            ) == user_result2.__getattribute__(attr), (
                f"The {attr} is {str(referenceUser2.__getattribute__(attr))} instead "
                f"of {user_result2.__getattribute__(attr)}."
            )


def test_newUser():
    referenceUser3 = User(
        username="testUser5",
        id=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-5",
        usergroups=["1", "2", "3"],
    )

    userManager.newUser(
        username=referenceUser3.username,
        password=referenceUser3.password,
        usergroups=referenceUser3.usergroups,
        userDB=test_config.userDB,
    )

    userDB = userManager.UserDB(test_config.userDB)

    user_result3 = userDB.getSingleUser(username=referenceUser3.username)

    for attr in referenceUser3.allAttributes():
        if attr == "password":
            assert userManager.verifyPassword(
                password=referenceUser3.__getattribute__(attr),
                passwordHash=user_result3.__getattribute__(attr),
            ), "The password of the user does not match the target."
        elif attr != "id":
            assert str(
                referenceUser3.__getattribute__(attr)
            ) == user_result3.__getattribute__(attr), (
                f"The {attr} is {str(referenceUser3.__getattribute__(attr))} instead "
                f"of {user_result3.__getattribute__(attr)}."
            )


def test_singleUser():
    db = userManager.UserDB(test_config.userDB)
    referenceUser4 = User(
        username="testUser6",
        id=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-6",
        usergroups=["1", "2", "3"],
    )
    db.addNewUser(referenceUser4)
    db.closeConnection()

    user_result4 = userManager.singleUser(
        username=referenceUser4.username, userDB=test_config.userDB
    )

    for attr in referenceUser4.allAttributes():
        if attr == "password":
            assert userManager.verifyPassword(
                password=referenceUser4.__getattribute__(attr),
                passwordHash=user_result4[attr],
            ), "The password of the user does not match the target."
        elif attr != "id":
            assert str(referenceUser4.__getattribute__(attr)) == user_result4[attr], (
                f"The {attr} is {user_result4[attr]} instead of "
                f"{str(referenceUser4.__getattribute__(attr))}."
            )


def test_allUsers():
    allUsers_reference2 = [
        User(
            username="testUser",
            id=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-",
            usergroups=["1", "2", "3"],
        ).to_dict(),
        User(
            username="testUser2",
            id=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-2",
            usergroups=["1", "2", "3"],
        ).to_dict(),
        User(
            username="testUser3",
            id=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-3",
            usergroups=["1", "2", "3"],
        ).to_dict(),
        User(
            username="testUser4",
            id=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-4",
            usergroups=["1", "2", "3"],
        ).to_dict(),
        User(
            username="testUser5",
            id=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-5",
            usergroups=["1", "2", "3"],
        ).to_dict(),
        User(
            username="testUser6",
            id=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-6",
            usergroups=["1", "2", "3"],
        ).to_dict(),
    ]

    allUsers_result2 = userManager.allUsers(userDB=test_config.userDB)

    assert all(
        [isinstance(u, dict) for u in allUsers_result2]
    ), "Not all objects in the obtained list of all users are of type User"

    # remove all passwords
    usernames_ref = []
    usernames_res = []
    for user_ref in allUsers_reference2:
        usernames_ref.append(user_ref["username"])
    for user_res in allUsers_result2:
        usernames_res.append(user_res["username"])

    for usernameReference in usernames_ref:
        assert usernameReference in usernames_res, (
            f"The entry {usernameReference} is not contained in the result "
            f"dictionary {usernames_res}."
        )


def test_getActiveUser():
    db = userManager.UserDB(test_config.userDB)
    referenceUser8 = User(
        username="testUser10",
        id=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-10",
        usergroups=["1", "2", "3"],
    )
    db.addNewUser(referenceUser8)
    db.closeConnection()

    expiration = datetime.timedelta(minutes=23)
    test_tokenData = {
        "sub": referenceUser8.username,
        "exp": datetime.datetime.now() + expiration,
    }
    keySecret = test_config.secretKey
    algo = test_config.algorithm

    tokenRefUser = jwt.encode(test_tokenData, keySecret, algorithm=algo)

    activeUser = userManager.getActiveUser(
        token=tokenRefUser, userDB=test_config.userDB
    )

    for attr in referenceUser8.allAttributes():
        if attr == "password":
            assert userManager.verifyPassword(
                password=referenceUser8.__getattribute__(attr),
                passwordHash=activeUser[attr],
            ), "The password of the user does not match the target."
        else:
            assert str(referenceUser8.__getattribute__(attr)) == activeUser[attr], (
                f"The {attr} is {activeUser[attr]} instead of "
                f"{str(referenceUser8.__getattribute__(attr))}."
            )


def test_hashPassword():
    testContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password_test = "TestPassword_0835-?"

    hashedPassword = userManager.hashPassword(password=password_test)

    assert testContext.verify(
        password_test, hashedPassword
    ), "The password could not be verified."


def test_verifyPassword():
    testContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password_test2 = "TestPassword_0835-?"

    hashedPassword2 = userManager.hashPassword(password=password_test2)

    assert testContext.verify(
        password_test2, hashedPassword2
    ) and userManager.verifyPassword(
        password=password_test2, passwordHash=hashedPassword2
    ), "The password could not be verified correctly."


def test_getAccessToken():
    db = userManager.UserDB(test_config.userDB)
    referenceUser6 = User(
        username="testUser8",
        id=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-8",
        usergroups=["1", "2", "3"],
    )
    db.addNewUser(referenceUser6)
    db.closeConnection()

    expiration = datetime.timedelta(minutes=23)
    test_tokenData = {
        "sub": referenceUser6.username,
        "exp": datetime.datetime.now() + expiration,
    }
    keySecret = test_config.secretKey
    algo = test_config.algorithm

    token_reference = jwt.encode(test_tokenData, keySecret, algorithm=algo)

    token_result = userManager.getAccessToken(
        tokenData=test_tokenData, expirationMin=expiration
    )

    assert (
        token_result == token_reference
    ), f"The resulting token is {token_result} instead of {token_reference}."


def test_userAuthentication():
    db = userManager.UserDB(test_config.userDB)
    referenceUser5 = User(
        username="testUser7",
        id=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-7",
        usergroups=["1", "2", "3"],
    )
    db.addNewUser(referenceUser5)
    db.closeConnection()

    user_result5 = userManager.userAuthentication(
        username=referenceUser5.username,
        password=referenceUser5.password,
        userDB=test_config.userDB,
    )

    for attr in referenceUser5.allAttributes():
        if attr == "password":
            assert userManager.verifyPassword(
                password=referenceUser5.__getattribute__(attr),
                passwordHash=user_result5.__getattribute__(attr),
            ), "The password of the user does not match the target."
        else:
            assert str(
                referenceUser5.__getattribute__(attr)
            ) == user_result5.__getattribute__(attr), (
                f"The {attr} is {user_result5.__getattribute__(attr)} instead of "
                f"{str(referenceUser5.__getattribute__(attr))}."
            )
