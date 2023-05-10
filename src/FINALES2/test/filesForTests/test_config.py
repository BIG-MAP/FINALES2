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
