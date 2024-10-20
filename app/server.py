import zlib
import hashlib
import tempfile
from .utility import *

__all__ = ["Server"]


class DFile:
    def __init__(self, data: bytes, passwd: bytes = b""):
        self.temp = tempfile.TemporaryFile()
        self.temp.write(zlib.compress(data))
        self.passwd = hashlib.sha256(passwd).digest()

    def closed(self):
        return self.temp is None

    def check(self, passwd: bytes = b""):
        return hashlib.sha256(passwd).digest() == self.passwd

    def close(self):
        if self.temp is None:
            return
        self.temp.close()
        self.temp = None

    def read(self):
        if self.temp is None:
            return b""
        self.temp.seek(0)
        return zlib.decompress(self.temp.read())


class Server:
    file_table: Dict[str, DFile]
    cmd_list: Dict[str, Tuple[str]] = {
        "test": (),
        "list": (),
        "insert": ("file", "data", "passwd"),
        "erase": ("file", "passwd"),
        "get": ("file", "passwd"),
    }

    def __init__(
        self,
        hostname: str = "localhost",
        post: int = 8080,
        backlog: int = 16,
        client_timeout: Union[float, None] = 0.2,
    ):
        self.file_table = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((hostname, post))
        self.server_socket.listen(backlog)
        self.timeout = client_timeout

    def list(self):
        return json.dumps(list(self.file_table))

    def insert(self, file: str, data: bytes, passwd: bytes = b""):
        if file in self.file_table:
            raise Exception("File already exist.")
        self.file_table[file] = DFile(data, passwd)

    def erase(self, file: str, passwd: bytes = b""):
        if file not in self.file_table:
            raise Exception("File does not exist.")
        df = self.file_table[file]
        if not df.check(passwd):
            raise Exception("Password error.")
        df.close()
        self.file_table.pop(file)

    def get(self, file: str, passwd: bytes = b""):
        if file not in self.file_table:
            raise Exception("File does not exist.")
        df = self.file_table[file]
        if not df.check(passwd):
            raise Exception("Password error.")
        return df.read()

    @staticmethod
    def check_data(data: str):
        args = json.loads(data)
        assert type(args) is dict, "Can't Decode Data"
        assert "type" in args, "Can't Decode Data"
        assert args["type"] in Server.cmd_list, "Can't Decode Data"
        for g in Server.cmd_list[args["type"]]:
            assert g in args and type(args[g]) is str, "Can't Decode Data"
        return args

    def server(self, client: socket.socket):
        client.settimeout(self.timeout)
        try:
            data = Server.check_data(recvs(client).decode())
            if data["type"] == "test":
                try_send(client, OK)
            elif data["type"] == "list":
                client.send(self.list().encode())
            elif data["type"] == "insert":
                self.insert(
                    data["file"],
                    data["data"].encode(),
                    data["passwd"].encode(),
                )
                try_send(client, OK)
            elif data["type"] == "erase":
                self.erase(
                    data["file"],
                    data["passwd"].encode(),
                )
                try_send(client, OK)
            elif data["type"] == "get":
                data = self.get(
                    data["file"],
                    data["passwd"].encode(),
                )
                client.send(data)
            else:
                raise Exception("Can't Decode Data")
        except Exception as err:
            print(str(err))
            try_send(client, str(err).encode())
        else:
            print("Ok")
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
        return thread
