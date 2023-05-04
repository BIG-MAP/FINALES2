import pathlib

scriptPath = pathlib.Path(__file__).parent.resolve()

host = "localhost"
port = 13371

userDB: str = "/root/data/FINALES2/src/FINALES2/test/filesForTests/session_testing.db"

# use openssl rand -hex 32 to generate the secret key
secretKey = "3e469b60dfb746971bdf440cd80306dca5c9469ab589aebbfaf213461b21e8cc"
algorithm = "HS256"
tokenExpirationMin = 2
