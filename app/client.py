from .utility import *


class Client:
    def __init__(
        self,
        hostname: str = "localhost",
        post: int = 8080,
        client_timeout: float = None,
    ):
        self.address = (hostname, post)
        self.timeout = CLI_TIMEOUT if client_timeout is None else client_timeout

    def requset_head(self, **data: str):
        cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cli.settimeout(self.timeout)
        cli.connect(self.address)
        cli.sendall(json.dumps(data).encode())
        return cli

    def test(self):
        cli = self.requset_head(type="test")
        code = cli.recv(BUFSIZE)
        cli.close()
        assert code == VERSION.encode(), VERSION_DIFF

    def list(self):
        cli = self.requset_head(type="list")
        res = json.loads(recvs(cli).decode())
        cli.close()
        assert type(res) is list
        return res

    def insert(
        self,
        filepath: str,
        passwd: str = "",
        *,
        callback: typing.Callable[[int, int], None] = lambda sent, size: None
    ):
        file = getFilename(filepath)
        cli = self.requset_head(type="insert", file=file, passwd=passwd)
        code = cli.recv(BUFSIZE)
        assert code == OK
        for p, q in send_file(cli, filepath):
            callback(p, q)
        code = cli.recv(BUFSIZE)
        return code.decode()

    def erase(self, file: str, passwd: str = ""):
        cli = self.requset_head(type="erase", file=file, passwd=passwd)
        code = cli.recv(BUFSIZE)
        cli.close()
        return code.decode()

    def get(self, file: str, passwd: str = ""):
        cli = self.requset_head(type="get", file=file, passwd=passwd)
        res = recvs(cli)
        cli.close()
        return res
