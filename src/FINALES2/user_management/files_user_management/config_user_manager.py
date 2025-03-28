# get the root for the paths
from pathlib import Path

from FINALES2.user_management.user_manager import new_user

script_path = Path(__file__).resolve().parent
# Information regarding the user database
# user_db: str = str(script_path / "add_your_database_name.db")
user_db: str = str(script_path / "db_skste_instance.db")
# Information regarding the authentication
secret_key = "FinalesTesterSimon"  # add your secret key
algorithm = "HS256"
token_expiration_min = 1440


new_user(username="Simon1", password=secret_key, usergroups=["group1", "group2"])
