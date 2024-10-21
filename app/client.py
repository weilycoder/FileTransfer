from .utility import *


class Client:
    def __init__(
        self,
        hostname: str = "localhost",
        post: int = 8080,
        *,
        client_timeout: float = None,
        bufsize: int = None
    ):
        self.address = (hostname, post)
        self.timeout = CLI_TIMEOUT if client_timeout is None else client_timeout
        self.bufsize = BUFSIZE if bufsize is None else bufsize

    @property
    def ver_info(self):
        return {"version": VERSION, "bufsize": self.bufsize}

    def send_file(self, fd: socket.socket, filename: str):
        with open(filename, "rb") as f:
            size = os.path.getsize(filename)
            head = hex(size).encode()
            assert len(head) <= self.bufsize, REQ_HEAD_TOO_LONG
            fd.send(head)
            code = fd.recv(self.bufsize)
            assert code == OK, FAIL_REQ
            sent = 0
            while True:
                data = f.read(self.bufsize)
                if not data:
                    break
                fd.send(data)
                sent += len(data)
                code = fd.recv(self.bufsize)
                assert code == CONT, FAIL_SEND
                yield (sent, size)

    def requset_head(self, **data: str):
        cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cli.settimeout(self.timeout)
        cli.connect(self.address)
        cli.sendall(json.dumps(data).encode())
        return cli

    def test(self):
        try:
            cli = self.requset_head(type="test")
            code = cli.recv(self.bufsize)
            code = json.loads(code.decode())
            assert code == self.ver_info
            cli.close()
        except AssertionError:
            raise Exception(SETTING_DIFF)

    def list(self):
        cli = self.requset_head(type="list")
        res = json.loads(recvs(cli, self.bufsize).decode())
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
        code = cli.recv(self.bufsize)
        if code != OK:
            return code.decode()
        for p, q in self.send_file(cli, filepath):
            if callback(p, q):
                cli.shutdown(socket.SHUT_WR)
                break
        code = cli.recv(self.bufsize)
        while code == CONT:
            code = cli.recv(self.bufsize)
        return code.decode()

    def erase(self, file: str, passwd: str = ""):
        cli = self.requset_head(type="erase", file=file, passwd=passwd)
        code = cli.recv(self.bufsize)
        cli.close()
        return code.decode()

    def get(self, file: str, passwd: str = ""):
        cli = self.requset_head(type="get", file=file, passwd=passwd)
        res = recvs(cli, self.bufsize)
        cli.close()
        return res
