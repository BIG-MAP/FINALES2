import json
import os
from pathlib import Path

from pydantic import BaseModel

# I think it is preferable to always put configuration stuff on the home
# folder, but due to how the docker container works (the volume only saves
# data that is inside the `/data` folder, which is not guaranteed to exist
# in general user setups/accounts) we now store it with the codebase.
#
SCRIPT_FOLDER = Path(__file__).resolve().parent
FINALES_CONFIG_FILEPATH_DEFAULT = SCRIPT_FOLDER / "config.json"
# FINALES_CONFIG_FILEPATH_DEFAULT = Path.home() / '.FINALES' / 'config.json'

DEFAULT_USERDB_PATH = SCRIPT_FOLDER.parent / "user_management"
DEFAULT_USERDB_PATH = DEFAULT_USERDB_PATH / "files_user_management"
DEFAULT_USERDB_PATH = DEFAULT_USERDB_PATH / "users.db"


class FinalesConfiguration(BaseModel):
    secret_key: str = ""
    user_db: str = str(DEFAULT_USERDB_PATH)
    algorithm: str = "HS256"
    token_expiration_min: int = 1440


def get_configuration():
    """Returns the dict with configuration for FINALES."""

    if "FINALES_CONFIG_FILEPATH" in os.environ:
        config_filepath = os.getenv("FINALES_CONFIG_FILEPATH")
        config_filepath = Path(config_filepath)
    else:
        config_filepath = FINALES_CONFIG_FILEPATH_DEFAULT

    if not config_filepath.exists():
        print(
            f"Config file {config_filepath} does not exist, creating it "
            f"(and parent folders) with default values."
        )
        parent_path = config_filepath.parent
        parent_path.mkdir(parents=True, exist_ok=True)
        default_config = FinalesConfiguration()
        default_config_data = default_config.dict()
        with open(config_filepath, "w") as fileobj:
            json.dump(default_config_data, fileobj, indent=2)
        return default_config

    with open(config_filepath) as fileobj:
        config_data = json.load(fileobj)
        config_object = FinalesConfiguration(**config_data)
        return config_object
