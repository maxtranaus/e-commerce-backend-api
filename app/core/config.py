import json
import os
from typing import Any


class Config:
    secret_key: str
    algorithm: str
    db_host: str
    db_port: str
    db_username: str
    db_password: str
    db_name: str


def read_config_file(filename: str) -> Config:
    filepath = os.path.join(os.path.dirname(__file__), f"../../{filename}")
    with open(filepath, "r") as file:
        data: dict[str, str] = json.load(file)
    config = Config()
    config.secret_key = data.get("secret_key", "Secretkey")
    config.algorithm = data.get("algorithm", "HS256")
    config.db_host = data.get("db_host", "localhost")
    config.db_port = data.get("db_port", "5432")
    config.db_username = data.get("db_username", "postgres")
    config.db_password = data.get("db_password", "password")
    config.db_name = data.get("db_name", "ecommerce")
    return config


def read_test_file(filename: str) -> dict[str, Any]:
    filepath = os.path.join(os.path.dirname(__file__), f"../../{filename}")
    with open(filepath, "r") as file:
        data: dict[str, str] = json.load(file)
    return data


config = read_config_file("config.json")
test_data = read_test_file("test_data.json")
