import sys
import argparse

try:
    from app import Server, UI, wait, CheckBigInt
except ImportError:
    from app import Server, UI, wait, CheckBigInt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Launch the File Transfer, which defaults to starting in client mode."
    )
    parser.add_argument(
        "-s", "--server", help="start in server mode", action="store_true"
    )
    parser.add_argument("-i", "--host", default="localhost", help="set the server name")
    parser.add_argument(
        "-p", "--post", default=8080, type=int, help="set the communication port"
    )
    parser.add_argument(
        "-b",
        "--buf",
        type=CheckBigInt(1024),
        help="set buffer size, which must be greater than or equal to 1024",
    )
    parser.add_argument("--timeout", type=float, help="set the timeout in second")
    parser.add_argument(
        "--backlog",
        default=16,
        type=int,
        help="Maximum number of connections, only effective when starting in server mode",
    )
    parser.add_argument(
        "--superpasswd",
        help="set a super password, only effective when starting in server mode",
    )
    args = parser.parse_args()
    try:
        if args.server:
            app = Server(
                super_passwd=args.superpasswd,
                hostname=args.host,
                post=args.post,
                backlog=args.backlog,
                client_timeout=args.timeout,
                bufsize=args.buf,
            )
            app.start()
            wait()
        else:
            app = UI(
                host=args.host,
                post=args.post,
                client_timeout=args.timeout,
                bufsize=args.buf,
            )
    except Exception as err:
        print(err, file=sys.stderr)
