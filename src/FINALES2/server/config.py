# get the root for the paths
import pathlib

script_path = pathlib.Path(__file__).resolve().parent


# Information regarding the operation of the MAP
sleepTime_s = 1

# Information regarding the user database
user_db: str = str(script_path / "userDB.db")
