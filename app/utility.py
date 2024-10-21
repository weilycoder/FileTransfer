import os
import json
import socket
import os.path
import threading

from typing import *

VERSION = "0.2.0"
VERSION_DIFF = "The server and client versions are different."

CLI_TIMEOUT = 4
SER_TIMEOUT = 0.2
BUFSIZE = 1048576

OK = b"Ok."
CONT = "CONT."

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


def recvs(client: socket.socket):
    data = bytearray()
    while True:
        d0 = try_recv(client, BUFSIZE)
        if not d0:
            break
        data.extend(d0)
    return data


def getFilename(path: str):
    return path.replace("\\", "/").split("/")[-1]


def send_file(fd: socket.socket, filename: str):
    with open(filename, "rb") as f:
        size = os.path.getsize(filename)
        head = hex(size).encode()
        assert len(head) <= BUFSIZE, REQ_HEAD_TOO_LONG
        fd.send(head)
        code = fd.recv(BUFSIZE)
        assert code == OK, FAIL_REQ
        sent = 0
        while True:
            data = f.read(BUFSIZE)
            if not data:
                break
            fd.send(data)
            sent += len(data)
            code = fd.recv(BUFSIZE)
            assert code == OK, FAIL_SEND
            yield (sent, size)


def recv_file(fd: socket.socket, file: BinaryIO):
    size = int(fd.recv(BUFSIZE), 16)
    fd.send(OK)
    sent = 0
    while sent < size:
        data = fd.recv(BUFSIZE)
        if not data:
            break
        sent += len(data)
        fd.send(OK)
        file.write(data)
        yield sent, size
    assert sent == size, FAIL_LEN
