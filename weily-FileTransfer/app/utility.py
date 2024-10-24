import io
import os
import sys
import time
import json
import socket
import os.path
import threading
import traceback
import typing

from typing import *  # type: ignore
from functools import wraps


VERSION = "0.2.1"
VERSION_DIFF = "The server and client versions are different."
SETTING_DIFF = "The communication settings between the server and client are different."

CLI_TIMEOUT = 4
SER_TIMEOUT = 4
BUFSIZE = 65536

OK = b"Ok."
CONT = b"CONT."

CANT_READ = "Can't Decode Data"
PASSWD_ERR = "Password error."
FILE_EXIST = "File already exist."
FILE_NOT_EXIST = "File does not exist."

REQ_HEAD_TOO_LONG = "Request header too long."
FAIL_REQ = "Request failed."
FAIL_SEND = "Send failed."
FAIL_LEN = "Length verification failed."

INFO = "[INFO]"
WARN = "[WARN]"

UI_BLOCK = 100


class Loggers:
    def __init__(self, file: typing.TextIO = sys.stderr):
        self.file = file

    @staticmethod
    def ftime():
        return f"{time.strftime('%Y-%m-%dT%H:%M:%S%z')} {time.monotonic():.3f}"

    def err_logger(self, error: BaseException):
        print(self.ftime())
        print(*traceback.format_exception(type(error), error, error.__traceback__))

    def log_logger(self, *args, before: Optional[str] = None):
        if before is None:
            print(self.ftime(), *args)
        else:
            print(before, self.ftime(), *args)


stdloggers = Loggers()


def try_recv(client: socket.socket, bufsize: int):
    try:
        return client.recv(bufsize)
    except OSError:
        return b""


def try_send(client: socket.socket, msg: bytes):
    try:
        client.sendall(msg)
    except OSError:
        pass


def safe_send_head(client: socket.socket, msg: bytes, bufsize: int):
    assert len(msg) <= bufsize, REQ_HEAD_TOO_LONG
    try_send(client, msg)


def recvs(client: socket.socket, bufsize: int):
    data = bytearray()
    while True:
        d0 = try_recv(client, bufsize)
        if not d0:
            break
        data.extend(d0)
    return data


def getFilename(path: str):
    return path.replace("\\", "/").split("/")[-1]


def withThread(function: Callable[..., Any]):
    @wraps(function)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(
            target=function, args=args, kwargs=kwargs, daemon=True
        )
        thread.start()
        return thread

    return wrapper


def logException(logger: Callable[..., None]):
    def decorator(function: Callable[..., Any]):
        @wraps(function)
        def warpper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except BaseException as err:
                logger(err)

        return warpper

    return decorator


def is_instance_of(obj: Any, type_annotation: Any) -> bool:
    if type_annotation is ... or isinstance(type_annotation, TypeVar):
        return True

    if not hasattr(type_annotation, "__origin__"):
        return isinstance(obj, type_annotation)

    origin = type_annotation.__origin__
    args = type_annotation.__args__

    if origin is list or origin is List:
        return isinstance(obj, list) and all(
            is_instance_of(item, args[0]) for item in obj
        )

    if origin is dict or origin is Dict:
        key_type, value_type = args
        return isinstance(obj, dict) and all(
            is_instance_of(k, key_type) and is_instance_of(v, value_type)
            for k, v in obj.items()
        )

    if origin is tuple or origin is Tuple:
        if len(args) == 2 and args[1] is ...:
            return isinstance(obj, tuple) and all(
                is_instance_of(item, args[0]) for item in obj
            )
        else:
            return (
                isinstance(obj, tuple)
                and len(obj) == len(args)
                and all(is_instance_of(item, arg) for item, arg in zip(obj, args))
            )

    if origin is set or origin is Set:
        return isinstance(obj, set) and all(
            is_instance_of(item, args[0]) for item in obj
        )

    if origin is frozenset or origin is FrozenSet:
        return isinstance(obj, frozenset) and all(
            is_instance_of(item, args[0]) for item in obj
        )

    if origin is Union:
        return any(is_instance_of(obj, arg) for arg in args)

    return False


def ignoreExceptions(
    error: Union[Type[BaseException], Tuple[Type[BaseException], ...]],
    codeWhenError: Any = None,
):
    def decorator(function: Callable[..., Any]):
        @wraps(function)
        def warpper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except error:
                return codeWhenError

        return warpper

    return decorator


@ignoreExceptions(KeyboardInterrupt)
def wait():
    while True:
        pass


def CheckBigInt(start: int):
    def checker(val: Any):
        x = int(val)
        if x < start:
            raise ValueError
        return x

    return checker
