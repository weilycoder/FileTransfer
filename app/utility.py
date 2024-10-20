import json
import socket
import threading

from typing import *


HEADSIZE = 8
BUFSIZE = 65536
OK = b"Ok"
NEXT = b"Next"


def try_recv(client: socket.socket, bufsize: int):
    try:
        return client.recv(bufsize)
    except:
        return b""


def try_send(client: socket.socket, msg: bytes):
    try:
        client.send(msg)
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
