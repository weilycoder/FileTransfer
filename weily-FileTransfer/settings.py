import argparse
import tomlkit
import tomlkit.exceptions

from typing import *  # type: ignore

try:
    from app import stdloggers
except ImportError:
    from .app import stdloggers


CLIENT = "client"
SERVER = "server"
MODE_CHOICES = (CLIENT, SERVER)
DEFAULT_SETTING = {
    "mode": "client",
    "client": {"host": "localhost", "post": 8080},
    "server": {"host": "0.0.0.0", "post": 8080},
}


def CheckBigInt(start: int, name: Optional[str]):
    def checker(val: Any):
        x = int(val)
        if x < start:
            raise ValueError
        return x

    if name is not None:
        checker.__name__ = name
    return checker


def read_toml(filename: str):
    try:
        with open(filename, "r") as fd:
            return tomlkit.load(fd)
    except (FileNotFoundError, tomlkit.exceptions.TOMLKitError):
        return DEFAULT_SETTING


def save_toml(filename: str, setting: Dict[str, Any]):
    with open(filename, "w") as fd:
        tomlkit.dump(setting, fd)


def get_setting(args: argparse.Namespace, toml_file: str) -> Dict[str, Any]:
    setting = DEFAULT_SETTING.copy()
    try:
        toml_setting = read_toml(toml_file)
        if "mode" in toml_setting:
            assert toml_setting["mode"] in MODE_CHOICES
            setting["mode"] = toml_setting["mode"]
        if "server" in toml_setting:
            assert isinstance(toml_setting["server"], dict)
            setting["server"].update(toml_setting["server"])
        if "client" in toml_setting:
            assert isinstance(toml_setting["client"], dict)
            setting["client"].update(toml_setting["client"])
    except AssertionError:
        stdloggers.warn_logger("Configuration file parsing failed.")
        setting = DEFAULT_SETTING.copy()
    argv_setting = vars(args)
    mode = str(argv_setting["mode"] or setting["mode"])
    setting["mode"] = mode
    argv_setting.pop("mode")
    for k, v in argv_setting.items():
        if v is not None:
            setting[mode][k] = v
    save_toml(toml_file, setting)
    ret = {"mode": mode}
    ret.update(setting[mode])
    return ret


class Settings:
    def __init__(self, setting: Dict[str, Any]):
        self.__setting = setting

    def __getattribute__(self, name: str):
        if name[:1] == "_":
            return super().__getattribute__(name)
        return self.__setting.get(name, None)
