import os
import yaml
import joblib

from pathlib import Path
from box import Box
from box.exceptions import BoxValueError

from ServicenowGamification import logger


class ConfigBox(Box):
    def __getattr__(self, item):
        if item not in self:
            raise AttributeError(
                f"Key '{item}' not found in ConfigBox"
            )
        return super().__getattr__(item)


def Read_Yaml(path_to_yaml: Path) -> ConfigBox:

    try:

        path_to_yaml = Path(path_to_yaml)

        print(f"Reading YAML : {path_to_yaml}")

        if not path_to_yaml.exists():
            raise FileNotFoundError(
                f"YAML file does not exist -> {path_to_yaml}"
            )

        with open(path_to_yaml, "r", encoding="utf-8-sig") as yaml_file:
            content = yaml.safe_load(yaml_file)

        if content is None:
            content = {}

        logger.info(
            f"YAML file loaded successfully : {path_to_yaml}"
        )

        return ConfigBox(content)

    except BoxValueError:
        raise ValueError(
            f"Error reading YAML file : {path_to_yaml}"
        )

    except Exception as e:
        raise e


def create_directories(paths: list, verbose=True):

    for path in paths:
        #print(f"Received path : {path}")
        os.makedirs(path, exist_ok=True)
        #print(f"Directory exists : {Path(path).exists()}")
        #print(f"Absolute path : {Path(path).resolve()}")

        if verbose:
            logger.info(
                f"Created directory : {path}"
            )


def get_size(path: Path) -> str:

    size_in_kb = round(
        os.path.getsize(path) / 1024
    )

    return f"~{size_in_kb} KB"


def save_object(file_path: Path, obj):

    try:

        file_path = Path(file_path)

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        joblib.dump(obj, file_path)

        logger.info(
            f"Object saved at : {file_path}"
        )

    except Exception as e:
        raise e


def load_object(file_path: Path):

    try:

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"File not found : {file_path}"
            )

        return joblib.load(file_path)

    except Exception as e:
        raise e