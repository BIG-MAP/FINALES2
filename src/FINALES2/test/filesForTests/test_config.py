import pathlib

script_path = pathlib.Path(__file__).parent.resolve()

host = "localhost"
port = 13371

user_db: str = "/root/data/FINALES2/src/FINALES2/test/filesForTests/session_testing.db"

# use openssl rand -hex 32 to generate the secret key
secret_key = "3e469b60dfb746971bdf440cd80306dca5c9469ab589aebbfaf213461b21e8cc"
algorithm = "HS256"
token_expiration_min = 2


config_path = pathlib.Path(
    "/root/data/FINALES2/src/FINALES2/user_management/files_user_management"
)
if not config_path.is_dir():
    config_path.mkdir()
    with open(config_path.joinpath("config_user_manager.py"), "w") as config_file:
        config_file.write(
            """
import pathlib
script_path = pathlib.Path(__file__).resolve().parent

user_db: str = "/root/data/FINALES2/src/FINALES2/test/filesForTests/session_testing.db"

secret_key = "3e469b60dfb746971bdf440cd80306dca5c9469ab589aebbfaf213461b21e8cc"
algorithm = "HS256"
token_expiration_min = 1440
        """
        )
