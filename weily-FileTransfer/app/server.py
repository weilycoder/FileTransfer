import hashlib
import tempfile
from .utility import *


def checkHash(passwd: bytes, hash: bytes):
    return hashlib.sha256(passwd).digest() == hash


class DFile:
    super_passwd = b""

    def __init__(self, passwd: bytes = b""):
        self.temp = tempfile.TemporaryFile()
        self.passwd = hashlib.sha256(passwd).digest()

    @staticmethod
    def set_super_passwd(passwd: bytes):
        DFile.super_passwd = hashlib.sha256(passwd).digest()

    @property
    def filesize(self):
        if self.temp is None:
            return 0
        self.temp.flush()
        return os.fstat(self.temp.fileno()).st_size

    @property
    def no_passwd(self):
        return checkHash(b"", self.passwd)

    def closed(self):
        return self.temp is None

    def check(self, passwd: bytes = b""):
        return (
            self.no_passwd
            or checkHash(passwd, self.passwd)
            or checkHash(passwd, DFile.super_passwd)
        )

    def close(self):
        if self.temp is None:
            return
        self.temp.close()
        self.temp = None

    def read(self):
        if self.temp is None:
            return b""
        self.temp.flush()
        new_fd = os.dup(self.temp.fileno())
        with os.fdopen(new_fd, "rb") as f:
            f.seek(0)
            return self.temp.read()


class Server:
    file_table: Dict[str, DFile]

    def __init__(
        self,
        hostname: str = "localhost",
        post: int = 8080,
        backlog: int = 16,
        client_timeout: Optional[float] = None,
        *,
        super_passwd: Optional[str] = None,
        bufsize: Optional[int] = None,
        logger: Callable[..., Any] = stdloggers.log_logger,
    ):
        self.file_table = {}
        self.file_pre = set()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((hostname, post))
        self.server_socket.listen(backlog)
        self.timeout = client_timeout if client_timeout is not None else SER_TIMEOUT
        self.bufsize = BUFSIZE if bufsize is None else bufsize
        self.logger = logger
        if super_passwd is not None:
            DFile.set_super_passwd(super_passwd.encode())

    @property
    def ver_info(self):
        return {"version": VERSION, "bufsize": self.bufsize}

    def recv_file(self, fd: socket.socket, file: typing.BinaryIO):
        size = int(fd.recv(self.bufsize), 16)
        fd.send(OK)
        sent = 0
        while sent < size:
            data = fd.recv(self.bufsize)
            sent += len(data)
            fd.send(CONT)
            if not data:
                break
            file.write(data)
            yield sent, size
        assert sent == size, FAIL_LEN

    def get_list(self):
        return [(k, self.file_table[k].filesize) for k in self.file_table.copy()]

    def REQ_test(self, client: socket.socket, type: str):
        client.sendall(json.dumps(self.ver_info).encode())

    def REQ_list(self, client: socket.socket, type: str):
        client.sendall(json.dumps(self.get_list()).encode())

    def REQ_insert(
        self, client: socket.socket, type: str, *, file: str, passwd: str = ""
    ):
        assert file not in self.file_table and file not in self.file_pre, FILE_EXIST
        try:
            self.file_pre.add(file)
            fd = DFile(passwd.encode())
            ns = str(client.getpeername())
            client.send(OK)
            for p, q in self.recv_file(client, fd.temp):  # type: ignore
                self.logger(ns, f"{p}/{q}")
            self.file_table[file] = fd
            client.sendall(OK)
        finally:
            self.file_pre.remove(file)

    def REQ_erase(
        self, client: socket.socket, type: str, *, file: str, passwd: str = ""
    ):
        assert file in self.file_table, FILE_NOT_EXIST
        assert self.file_table[file].check(passwd.encode()), PASSWD_ERR
        self.file_table.pop(file).close()
        client.sendall(OK)

    def REQ_get(self, client: socket.socket, type: str, *, file: str, passwd: str = ""):
        assert file in self.file_table, FILE_NOT_EXIST
        dF = self.file_table[file]
        assert dF.check(passwd.encode()), PASSWD_ERR
        client.sendall(dF.read() + b"\0")

    def server(self, client: socket.socket):
        ns = str(client.getpeername())
        client.settimeout(self.timeout)
        try:
            head = json.loads(client.recv(self.bufsize).decode())
            assert type(head) is dict, CANT_READ
            assert "type" in head, CANT_READ
            assert type(head["type"]) is str, CANT_READ
            self.logger(ns, f"Req: {head['type']}")
            self.__getattribute__("REQ_" + head["type"])(client, **head)
        except (TypeError, AttributeError) as err:
            self.logger(ns, err)
            try_send(client, CANT_READ.encode())
        except Exception as err:
            self.logger(ns, str(err))
            try_send(client, str(err).encode())
        else:
            self.logger(ns, "Ok.")
        finally:
            client.close()

    def start(self):
        def listener():
            while True:
                try:
                    threading.Thread(
                        target=self.server,
                        args=(self.server_socket.accept()[0],),
                        daemon=True,
                    ).start()
                except (socket.timeout, TimeoutError):
                    pass

        thread = threading.Thread(target=listener, daemon=True)
        thread.start()
        self.logger("Start: ", self.ver_info)
        return thread
