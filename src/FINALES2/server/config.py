# get the root for the paths
import pathlib

scriptPath = pathlib.Path(__file__).parents[1].resolve()


# Info about the FINALES2 server
host = "0.0.0.0"
port = 13371

# Information regarding the user database
userDB: str = str(scriptPath / "userManagement" / "userDB.db")
salt_userDB = "dcf832f0ec6a80dc36afdO"

# Information regarding the authentication
# use openssl rand -hex 32 to get a random secret key
secretKey = "3e469b60dfb746971bdf440cd80306dca5c9469ab589aebbfaf213461b21e8cc"
algorithm = "HS256"
tokenExpirationMin = 2

# Information regarding the operation of the MAP
sleepTime_s = 1
