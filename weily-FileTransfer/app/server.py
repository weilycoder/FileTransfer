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
        client_timeout: Optional[float] = None,
        *,
        super_passwd: Optional[str] = None,
        bufsize: Optional[int] = None,
    ):
        self.file_table = {}
        self.file_pre = set()
        self.addr = (hostname, post)
        self.timeout = client_timeout if client_timeout is not None else SER_TIMEOUT
        self.bufsize = BUFSIZE if bufsize is None else bufsize
        if super_passwd is not None:
            DFile.set_super_passwd(super_passwd.encode())

    @property
    def ver_info(self):
        return {"version": VERSION, "bufsize": self.bufsize}

    async def recv(self, reader: asyncio.StreamReader):
        return await asyncio.wait_for(reader.read(self.bufsize), timeout=self.timeout)

    async def send(self, writer: asyncio.StreamWriter, data: bytes):
        try:
            writer.write(data)
            await writer.drain()
        except (ConnectionError, BrokenPipeError) as err:
            stdloggers.err_logger(err)

    async def recv_file(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        file: typing.BinaryIO,
    ):
        size = int(await self.recv(reader), 16)
        await self.send(writer, OK)
        sent = 0
        while sent < size:
            data = await self.recv(reader)
            sent += len(data)
            await self.send(writer, CONT)
            if not data:
                break
            file.write(data)
            yield sent, size
        assert sent == size, FAIL_LEN

    async def get_list(self):
        return [(k, self.file_table[k].filesize) for k in self.file_table.copy()]

    async def REQ_test(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, type: str
    ):
        await self.send(writer, json.dumps(self.ver_info).encode())

    async def REQ_list(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, type: str
    ):
        await self.send(writer, json.dumps(await self.get_list()).encode())

    async def REQ_insert(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        type: str,
        *,
        file: str,
        passwd: str = "",
    ):
        assert file not in self.file_table and file not in self.file_pre, FILE_EXIST
        try:
            self.file_pre.add(file)
            fd = DFile(passwd.encode())
            addr: Tuple[str, int] = writer.get_extra_info("peername")
            await self.send(writer, OK)
            async for p, q in self.recv_file(reader, writer, fd.temp):  # type: ignore
                stdloggers.log_logger(addr, f"{p}/{q}")
            self.file_table[file] = fd
            await self.send(writer, OK)
        finally:
            self.file_pre.remove(file)

    async def REQ_erase(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        type: str,
        *,
        file: str,
        passwd: str = "",
    ):
        assert file in self.file_table, FILE_NOT_EXIST
        assert self.file_table[file].check(passwd.encode()), PASSWD_ERR
        self.file_table.pop(file).close()
        await self.send(writer, OK)

    async def REQ_get(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        type: str,
        *,
        file: str,
        passwd: str = "",
    ):
        assert file in self.file_table, FILE_NOT_EXIST
        dF = self.file_table[file]
        assert dF.check(passwd.encode()), PASSWD_ERR
        await self.send(writer, dF.read() + b'\0')

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        addr: Tuple[str, int] = writer.get_extra_info("peername")
        try:
            head = json.loads(await self.recv(reader))
            assert type(head) is dict, CANT_READ
            assert "type" in head, CANT_READ
            assert type(head["type"]) is str, CANT_READ
            stdloggers.log_logger(addr, f"Req: {head['type']}")
            await self.__getattribute__("REQ_" + head["type"])(reader, writer, **head)
        except (TypeError, AttributeError) as err:
            stdloggers.warn_logger(addr, err)
            await self.send(writer, CANT_READ.encode())
        except TimeoutError as err:
            await self.send(writer, TIMED_OUT.encode())
        except Exception as err:
            stdloggers.warn_logger(addr, str(err))
            await self.send(writer, str(err).encode())
        else:
            stdloggers.log_logger(addr, OK)
        finally:
            writer.close()
            await writer.wait_closed()

    async def start(self):
        server = await asyncio.start_server(self.handle_client, *self.addr)
        stdloggers.log_logger("Start:", self.ver_info)

        async with server:
            await server.serve_forever()
