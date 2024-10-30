import argparse
import tomlkit

from typing import *  # type: ignore


UA_PAR = "Unable to parse configuration file (key: {key})"
CLIENT = "client"
SERVER = "server"
MODE_CHOICES = (CLIENT, SERVER)
DEFAULT_SETTING = {
    "mode": "client",
    "client": {"host": "localhost", "post": 8080},
    "server": {"host": "0.0.0.0", "post": 8080},
}


def CheckBigInt(start: int, name: Optional[str] = None):
    def checker(val: Any):
        x = int(val)
        if x < start:
            raise ValueError
        return x

    if name is not None:
        checker.__name__ = name
    return checker


SETTING_TYPE = {
    "host": str,
    "post": int,
    "buf": CheckBigInt(1024),
    "timeout": float,
    "superpasswd": str,
}


def read_toml(filename: str) -> Dict[str, Any]:
    try:
        with open(filename, "r") as fd:
            return tomlkit.load(fd)
    except FileNotFoundError:
        return DEFAULT_SETTING


def save_toml(filename: str, setting: Dict[str, Any]):
    with open(filename, "w") as fd:
        tomlkit.dump(setting, fd)


def get_setting(args: argparse.Namespace, toml_file: str) -> Dict[str, Any]:
    setting = DEFAULT_SETTING.copy()
    toml_setting = read_toml(toml_file)
    if "mode" in toml_setting:
        assert toml_setting["mode"] in MODE_CHOICES, UA_PAR.format(key="mode")
        setting["mode"] = toml_setting["mode"]
    if "server" in toml_setting:
        assert isinstance(toml_setting["server"], dict), UA_PAR.format(key="server")
        for k, v in toml_setting["server"].items():
            assert k in SETTING_TYPE, UA_PAR.format(key=k)
            try:
                setting["server"][k] = SETTING_TYPE[k](v)
            except ValueError:
                raise AssertionError(UA_PAR.format(key=k))
    if "client" in toml_setting:
        assert isinstance(toml_setting["client"], dict), UA_PAR.format(key="client")
        for k, v in toml_setting["client"].items():
            assert k in SETTING_TYPE, UA_PAR.format(key=k)
            try:
                setting["client"][k] = SETTING_TYPE[k](v)
            except ValueError:
                raise AssertionError(UA_PAR.format(key=k))
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
