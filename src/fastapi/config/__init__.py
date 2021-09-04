import sys
import os
from pathlib import Path

sys.path.append(str(Path(os.getcwd()) / "src"))
from src.fastapi.config.config import config_values


class Config:
    pass


def compose_config(
    existing_config: object = None, config_values: dict = config_values
) -> object:
    config = Config() if existing_config is None else existing_config
    [setattr(config, key, value) for key, value in config_values.items()]
    return config


def config_factory() -> object:
    return compose_config()


config = config_factory()
