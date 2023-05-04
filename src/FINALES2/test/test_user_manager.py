import datetime
from glob import glob
from os import remove
from sqlite3 import ProgrammingError
from uuid import UUID

from jose import jwt
from passlib.context import CryptContext
from pytest import raises

from FINALES2.test.filesForTests import test_config
from FINALES2.user_management import User, user_manager


def test_UserDB_init():
    # Get the path to the folder, where the user database is stored from the config file
    filepath = "/".join(test_config.userDB.split("/")[0:-1])
    print(filepath)

    # Delete potentially existing user databases
    for file in glob(f"{filepath}/*.db"):
        remove(file)

    # Test Case 1: New user database

    # Create the user database
    db = user_manager.UserDB(test_config.userDB)

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
    db.close_connection()

    # Test Case 2: Work with existing database

    # Reconnect to the existing database
    db = user_manager.UserDB(test_config.userDB)

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
    db.close_connection()


def test_UserDB_close_connection():
    # Connect to the user database or create a new one
    db = user_manager.UserDB(test_config.userDB)
    db.close_connection()

    with raises(ProgrammingError):
        db.cursor.execute("SELECT * FROM users")


def test_UserDB_add_new_user():
    db = user_manager.UserDB(test_config.userDB)
    user = User(
        username="testUser",
        uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-",
        usergroups=["1", "2", "3"],
    )
    print(user.__dict__)
    db.add_new_user(user)

    db.connect()

    data_result = db.cursor.execute("SELECT * FROM users").fetchone()
    data_target = tuple(list(str(v) for v in user.__dict__.values()))

    for i in range(4):
        if i != 2:
            data_result[i] == data_target[
                i
            ], f"The found data is {data_result[i]} instead of {data_target[i]}."
        else:
            data_result[i] == user_manager.hash_password(data_target[i]), (
                f"The found data is {user_manager.hash_password(data_result[i])} "
                f"instead of {data_target[i]}."
            )
    # TODO: check the timestamps#, '2023-01-14 17:06:17.416907'
    # , '2023-01-14 17:06:17.416907')]
    db.close_connection()


def test_UserDB_userFromRow():
    db = user_manager.UserDB(test_config.userDB)
    referenceUser = User(
        username="testUser2",
        uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-2",
        usergroups=["1", "2", "3"],
    )
    db.add_new_user(referenceUser)

    db.connect()

    aUser = db.cursor.execute(
        "SELECT * FROM users WHERE username=(?)", (referenceUser.username,)
    )
    row = aUser.fetchall()

    theUser = db.user_from_row(row[0])

    assert isinstance(theUser, User), (
        f"The object obtained from the userFromRow method is of "
        f"type {type(theUser)}instead of User."
    )

    for key in row[0].keys():
        if ("password" not in key) and ("timestamp" not in key):
            assert str(getattr(theUser, key)) == row[0][key], (
                f"The {key} of the object differs from the row. It is "
                f"{getattr(theUser, key)} instead of {row[0][key]}."
            )

    db.close_connection()


def test_UserDB_get_single_user():
    db = user_manager.UserDB(test_config.userDB)
    referenceUser = User(
        username="testUser3",
        uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-3",
        usergroups=["1", "2", "3"],
    )
    db.add_new_user(referenceUser)

    user_result = db.get_single_user(username=referenceUser.username)

    db.close_connection()

    for attr in referenceUser.__dict__.keys():
        if attr == "password":
            assert user_manager.verify_password(
                password=referenceUser.__getattribute__(attr),
                password_hash=user_result.__getattribute__(attr),
            )
        else:
            assert referenceUser.__getattribute__(attr) == user_result.__getattribute__(
                attr
            )


def test_UserDB_get_all_users():
    db = user_manager.UserDB(test_config.userDB)
    all_users_result = db.get_all_users()
    all_users_reference = [
        User(
            username="testUser",
            uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-",
            usergroups=["1", "2", "3"],
        ),
        User(
            username="testUser2",
            uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-2",
            usergroups=["1", "2", "3"],
        ),
        User(
            username="testUser3",
            uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-3",
            usergroups=["1", "2", "3"],
        ),
    ]

    assert all(
        [isinstance(u, User) for u in all_users_result]
    ), "Not all objects in the obtained list of all users are of type User"

    print(all_users_result)
    print(all_users_reference)

    for i in range(len(all_users_reference)):
        assert (
            all_users_reference[i].username == all_users_result[i].username
        ), f"The username is {all_users_result[i].username} "
        "instead of {all_users_reference[i].username}."
        assert (
            all_users_reference[i].uuid == all_users_result[i].uuid
        ), f"The uuid is {all_users_result[i].uuid} instead "
        "of {all_users_reference[i].uuid}."
        assert user_manager.verify_password(
            all_users_reference[i].password, all_users_result[i].password
        ), "The passwords to not match."


def test_create_user():
    referenceUser2 = User(
        username="testUser4",
        uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-4",
        usergroups=["1", "2", "3"],
    )

    user_result2 = user_manager.create_user(
        username=referenceUser2.username,
        password=referenceUser2.password,
        usergroups=referenceUser2.usergroups,
    )

    for attr in referenceUser2.__dict__.keys():
        if attr == "password":
            assert user_manager.verify_password(
                password=referenceUser2.__getattribute__(attr),
                password_hash=user_result2.__getattribute__(attr),
            ), "The password of the user does not match the target."
        elif attr != "uuid":
            assert str(referenceUser2.__getattribute__(attr)) == str(
                user_result2.__getattribute__(attr)
            ), (
                f"The {attr} is {str(referenceUser2.__getattribute__(attr))} instead "
                f"of {user_result2.__getattribute__(attr)}."
            )


def test_new_user():
    referenceUser3 = User(
        username="testUser5",
        uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-5",
        usergroups=["1", "2", "3"],
    )

    user_manager.new_user(
        username=referenceUser3.username,
        password=referenceUser3.password,
        usergroups=referenceUser3.usergroups,
    )

    userDB = user_manager.UserDB(test_config.userDB)

    user_result3 = userDB.get_single_user(username=referenceUser3.username)

    for attr in referenceUser3.__dict__.keys():
        if attr == "password":
            assert user_manager.verify_password(
                password=referenceUser3.__getattribute__(attr),
                password_hash=user_result3.__getattribute__(attr),
            ), "The password of the user does not match the target."
        elif attr != "uuid":
            assert str(referenceUser3.__getattribute__(attr)) == str(
                user_result3.__getattribute__(attr)
            ), (
                f"The {attr} is {str(referenceUser3.__getattribute__(attr))} instead "
                f"of {user_result3.__getattribute__(attr)}."
            )


def test_single_user():
    db = user_manager.UserDB(test_config.userDB)
    referenceUser4 = User(
        username="testUser6",
        uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-6",
        usergroups=["1", "2", "3"],
    )
    db.add_new_user(referenceUser4)
    db.close_connection()

    user_result4 = user_manager.single_user(username=referenceUser4.username)

    for attr in referenceUser4.__dict__.keys():
        if attr == "password":
            assert user_manager.verify_password(
                password=referenceUser4.__getattribute__(attr),
                password_hash=user_result4[attr],
            ), "The password of the user does not match the target."
        elif attr != "id":
            assert referenceUser4.__getattribute__(attr) == user_result4[attr], (
                f"The {attr} is {user_result4[attr]} instead of "
                f"{str(referenceUser4.__getattribute__(attr))}."
            )


def test_all_users():
    all_users_reference2 = [
        User(
            username="testUser",
            uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-",
            usergroups=["1", "2", "3"],
        ).__dict__,
        User(
            username="testUser2",
            uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-2",
            usergroups=["1", "2", "3"],
        ).__dict__,
        User(
            username="testUser3",
            uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-3",
            usergroups=["1", "2", "3"],
        ).__dict__,
        User(
            username="testUser4",
            uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-4",
            usergroups=["1", "2", "3"],
        ).__dict__,
        User(
            username="testUser5",
            uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-5",
            usergroups=["1", "2", "3"],
        ).__dict__,
        User(
            username="testUser6",
            uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
            password="thisIs_@testPW-6",
            usergroups=["1", "2", "3"],
        ).__dict__,
    ]

    all_users_result2 = user_manager.all_users()

    assert all(
        [isinstance(u, dict) for u in all_users_result2]
    ), "Not all objects in the obtained list of all users are of type User"

    # remove all passwords
    usernames_ref = []
    usernames_res = []
    for user_ref in all_users_reference2:
        usernames_ref.append(user_ref["username"])
    for user_res in all_users_result2:
        usernames_res.append(user_res["username"])

    for usernameReference in usernames_ref:
        assert usernameReference in usernames_res, (
            f"The entry {usernameReference} is not contained in the result "
            f"dictionary {usernames_res}."
        )


def test_get_active_user():
    db = user_manager.UserDB(test_config.userDB)
    referenceUser8 = User(
        username="testUser10",
        uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-10",
        usergroups=["1", "2", "3"],
    )
    db.add_new_user(referenceUser8)
    db.close_connection()

    expiration = datetime.timedelta(minutes=23)
    test_tokenData = {
        "sub": referenceUser8.username,
        "exp": datetime.datetime.now() + expiration,
    }
    keySecret = test_config.secretKey
    algo = test_config.algorithm

    tokenRefUser = jwt.encode(test_tokenData, keySecret, algorithm=algo)

    activeUser = user_manager.get_active_user(token=tokenRefUser)

    for attr in referenceUser8.__dict__.keys():
        if attr == "password":
            assert user_manager.verify_password(
                password=referenceUser8.__getattribute__(attr),
                password_hash=activeUser[attr],
            ), "The password of the user does not match the target."
        else:
            assert referenceUser8.__getattribute__(attr) == activeUser[attr], (
                f"The {attr} is {activeUser[attr]} instead of "
                f"{str(referenceUser8.__getattribute__(attr))}."
            )


def test_hash_password():
    testContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password_test = "TestPassword_0835-?"

    hashedPassword = user_manager.hash_password(password=password_test)

    assert testContext.verify(
        password_test, hashedPassword
    ), "The password could not be verified."


def test_verify_password():
    testContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password_test2 = "TestPassword_0835-?"

    hashedPassword2 = user_manager.hash_password(password=password_test2)

    assert testContext.verify(
        password_test2, hashedPassword2
    ) and user_manager.verify_password(
        password=password_test2, password_hash=hashedPassword2
    ), "The password could not be verified correctly."


def test_get_access_token():
    db = user_manager.UserDB(test_config.userDB)
    referenceUser6 = User(
        username="testUser8",
        uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-8",
        usergroups=["1", "2", "3"],
    )
    db.add_new_user(referenceUser6)
    db.close_connection()

    expiration = datetime.timedelta(minutes=23)
    test_tokenData = {
        "sub": referenceUser6.username,
        "exp": datetime.datetime.now() + expiration,
    }
    keySecret = test_config.secretKey
    algo = test_config.algorithm

    token_reference = jwt.encode(test_tokenData, keySecret, algorithm=algo)

    token_result = user_manager.get_access_token(
        token_data=test_tokenData, expiration_min=expiration
    )

    assert (
        token_result == token_reference
    ), f"The resulting token is {token_result} instead of {token_reference}."


def test_user_authentication():
    db = user_manager.UserDB(test_config.userDB)
    referenceUser5 = User(
        username="testUser7",
        uuid=UUID("{12345678-1234-5678-1234-567812345678}"),
        password="thisIs_@testPW-7",
        usergroups=["1", "2", "3"],
    )
    db.add_new_user(referenceUser5)
    db.close_connection()

    user_result5 = user_manager.user_authentication(
        username=referenceUser5.username,
        password=referenceUser5.password,
    )

    for attr in referenceUser5.__dict__.keys():
        if attr == "password":
            assert user_manager.verify_password(
                password=referenceUser5.__getattribute__(attr),
                password_hash=user_result5.__getattribute__(attr),
            ), "The password of the user does not match the target."
        else:
            assert referenceUser5.__getattribute__(
                attr
            ) == user_result5.__getattribute__(attr), (
                f"The {attr} is {user_result5.__getattribute__(attr)} instead of "
                f"{str(referenceUser5.__getattribute__(attr))}."
            )
