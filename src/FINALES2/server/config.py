host = "localhost"
port = 13371

userDB: str = "src/FINALES2/userManagement/userDB.db"
salt_userDB = "dcf832f0ec6a80dc36afdO"

secretKey = "3e469b60dfb746971bdf440cd80306dca5c9469ab589aebbfaf213461b21e8cc"  # use openssl rand -hex 32 to get a random secret key
algorithm = "HS256"
tokenExpirationMin = 2


# ----------------------------
# from FINALES
# ----------------------------

# #values
# reset: bool = True
# db_file: str = f'session_testing.db'
# MAX_D = 7

# SECRET_KEY = "dcf832f0ec6a80dc36afd95422f0bb1f1c964d916a8c0d29b127d3246e4c88a6"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*7

# sleeptime = 5

# ratio_threshold = 0.01

# ratio_threshold = 0.01
