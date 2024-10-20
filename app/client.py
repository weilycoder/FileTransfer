from .utility import *


class Client:
    def __init__(
        self,
        hostname: str = "localhost",
        post: int = 8080,
        client_timeout: Union[float, None] = 4,
    ):
        self.address = (hostname, post)
        self.timeout = client_timeout if client_timeout is not None else 4

    def requset(self, data: Dict[str, str]):
        cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cli.settimeout(self.timeout)
        cli.connect(self.address)
        cli.sendall(json.dumps(data).encode())
        return cli

    def test(self):
        cli = self.requset({"type": "test"})
        code = cli.recv(BUFSIZE)
        cli.close()
        return code == OK

    def list(self):
        cli = self.requset({"type": "list"})
        res = json.loads(recvs(cli).decode())
        cli.close()
        assert type(res) is list
        return res

    def insert(self, file: str, data: str, passwd: str = ""):
        cli = self.requset(
            {"type": "insert", "file": file, "data": data, "passwd": passwd}
        )
        code = cli.recv(BUFSIZE)
        cli.close()
        return code.decode()

    def erase(self, file: str, passwd: str = ""):
        cli = self.requset({"type": "erase", "file": file, "passwd": passwd})
        code = cli.recv(BUFSIZE)
        cli.close()
        return code.decode()

    def get(self, file: str, passwd: str = ""):
        cli = self.requset({"type": "get", "file": file, "passwd": passwd})
        res = recvs(cli)
        cli.close()
        return res.decode()
