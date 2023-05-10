"""This file provides a configuration for testing only. The keys in this file must not
be used for deployment of the code."""

from pathlib import Path

script_path = Path(__file__).parent.resolve()

host = "localhost"
port = 13371

user_db: str = str(Path(script_path).joinpath("session_testing.db"))

secret_key = "for_test_only"
algorithm = "HS256"
token_expiration_min = 2


# The following code generates a test config file for the user management, which will
# then be used for the test. It is a copy of this configuration file as the methods
# enabling the authentication process use the configuration file in the config_path as
# a standard, which cannot be changed as a parameter to avoid the filepath of the
# user database being exposed in the docs
config_base_path = Path(script_path).parents[2]
print(config_base_path)

config_path = Path(config_base_path).joinpath("files_user_management")
if not config_path.is_dir():
    config_path.mkdir()
    with open(config_path.joinpath("config_user_manager.py"), "w") as config_file:
        config_file.write(
            f"""
script_path = {script_path}

user_db: str = {user_db}

secret_key = {secret_key}
algorithm = {algorithm}
token_expiration_min = {token_expiration_min}
        """
        )
