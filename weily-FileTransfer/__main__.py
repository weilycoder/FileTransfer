import sys
import argparse

try:
    from app import Server, UI, asyncio
except ImportError:
    from .app import Server, UI, asyncio

try:
    from settings import MODE_CHOICES, SERVER, CheckBigInt, get_setting, Settings
except ImportError:
    from .settings import MODE_CHOICES, SERVER, CheckBigInt, get_setting, Settings


TOML_FILE = "filetransfer.toml"


def get_path():
    return "/".join(sys.argv[0].replace("\\", "/").split("/")[0:-1])


def get_toml_file():
    return get_path() + "/" + TOML_FILE


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch the File Transfer.")
    parser.add_argument(
        "--mode",
        choices=MODE_CHOICES,
        help="Specify the launch mode, which defaults to starting in client mode.",
    )
    parser.add_argument(
        "-i",
        "--host",
        help="set the server name",
    )
    parser.add_argument(
        "-p",
        "--post",
        type=int,
        help="set the communication port",
    )
    parser.add_argument(
        "-b",
        "--buf",
        type=CheckBigInt(1024, "size"),
        help="set buffer size, which must be greater than or equal to 1024",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        help="set the timeout in second",
    )
    parser.add_argument(
        "--superpasswd",
        help="set a super password, only effective when starting in server mode",
    )
    args = Settings(get_setting(parser.parse_args(), get_toml_file()))
    try:
        if args.mode == SERVER:
            app = Server(
                super_passwd=args.superpasswd,
                hostname=args.host,
                post=args.post,
                client_timeout=args.timeout,
                bufsize=args.buf,
            )
            asyncio.run(app.start())
        else:
            app = UI(
                host=args.host,
                post=args.post,
                client_timeout=args.timeout,
                bufsize=args.buf,
            )
            app.mainloop()
    except Exception as err:
        # print(err, file=sys.stderr)
        raise
    except KeyboardInterrupt:
        print("^C", file=sys.stderr)
        sys.exit(0)
