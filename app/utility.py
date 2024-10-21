import os
import json
import socket
import os.path
import threading
import typing


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


def try_recv(client: socket.socket, bufsize: int):
    try:
        return client.recv(bufsize)
    except:
        return b""


def try_send(client: socket.socket, msg: bytes):
    try:
        client.sendall(msg)
    except:
        return -1
    else:
        return 0


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


def withThread(function: typing.Callable[..., typing.Any]):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(
            target=function, args=args, kwargs=kwargs, daemon=True
        )
        thread.start()
        return thread

    return wrapper
