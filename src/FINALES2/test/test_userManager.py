from FINALES2.test.filesForTests import test_config
from FINALES2.schemas import User
from FINALES2.userManagement import userManager

from glob import glob
from os import remove
from sqlite3 import ProgrammingError
from pytest import raises
from uuid import UUID

def test_UserDB_init():

    # Get the path to the folder, where the user database is stored from the config file
    filepath = test_config.userDB.split('\\')[0]
    
    # Delete potentially existing user databases
    for file in glob(f"{filepath}\\*.db"):
        remove(file)

    ## Test Case 1: New user database

    # Create the user database
    db = userManager.UserDB(test_config.userDB)

    # Get the target list of column names
    columns_target = list(User.__annotations__.keys()) + ["timestamp_added", "timestamp_lastEdited"]

    # Get the resulting list of column names
    allColumns = db.cursor.execute("SELECT * FROM users")
    columns_result = [element[0] for element in allColumns.description]
    
    # Check that all target column names are in the result column names
    for col in columns_target:
        assert col in columns_result, f"The target column name {col} is not in the resulting column names for the new database."

    # Close the connection to the database
    db.closeConnection()

    ## Test Case 2: Work with existing database

    # Reconnect to the existing database
    db = userManager.UserDB(test_config.userDB)

        # Get the resulting list of column names
    allColumns = db.cursor.execute("SELECT * FROM users")
    columns_result = [element[0] for element in allColumns.description]
    
    # Check that all target column names are in the result column names
    for col in columns_target:
        assert col in columns_result, f"The target column name {col} is not in the resulting column names for the existing user database."

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
    user = User(username='testUser', id=UUID('{12345678-1234-5678-1234-567812345678}'), password='thisIs_@testPW-', usergroups=['1', '2', '3'])
    print(user.__dict__)
    db.addNewUser(user)

    data_result = db.cursor.execute("SELECT * FROM users").fetchone()
    data_target = tuple(list(str(v) for v in user.to_dict().values()))

    for i in range(4):
        if i != 2:
            data_result[i] == data_target[i], f"The found data is {data_result[i]} instead of {data_target[i]}."
        else:
            data_result[i] == userManager.hashPassword(data_target[i]), f"The found data is {userManager.hashPassword(data_result[i])} instead of {data_target[i]}."
    # TODO: check the timestamps#, '2023-01-14 17:06:17.416907', '2023-01-14 17:06:17.416907')]
    db.closeConnection()


def test_UserDB_getSingleUser():
    db = userManager.UserDB(test_config.userDB)
    referenceUser = User(username='testUser2', id=UUID('{12345678-1234-5678-1234-567812345678}'), password='thisIs_@testPW-', usergroups=['1', '2', '3'])
    db.addNewUser(referenceUser)

    user_result = userManager.singleUser(username=referenceUser.username, password=referenceUser.password)
    
    db.closeConnection()
    
    for attr in referenceUser.all_fields():
        if attr == "password":
            assert userManager.hashPassword(referenceUser.__getattribute__(attr)) == user_result.__getattribute__(attr)
        else:
            assert str(referenceUser.__getattribute__(attr)) == user_result.__getattribute__(attr)


