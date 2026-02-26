from pathlib import Path
import yaml


class Struct:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, dict):
                self.__dict__[key] = Struct(**value)
            else:
                self.__dict__[key] = value


def loadSettings(path: Path):
    here = Path(__file__).resolve().parents[2] #gets a parent dir 2 levels up
    with open(here / path, 'r') as stream:
        config_dict = yaml.safe_load(stream)

    return Struct(**config_dict)