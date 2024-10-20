import sys
import argparse

from app import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch the File Transfer, which defaults to starting in client mode.")
    parser.add_argument(
        "-s", "--server", help="start in server mode", action="store_true"
    )
    parser.add_argument("-i", "--host", default="localhost", help="set the server name")
    parser.add_argument("-p", "--post", default=8080, type=int, help="set the communication port")
    parser.add_argument(
        "--superpasswd",
        help="set a super password, only effective when starting in server mode",
    )
    args = parser.parse_args()
    try:
        if args.server:
            app = Server(super_passwd=args.superpasswd, hostname=args.host, post=args.post)
            app.start()
            wait()
        else:
            app = UI(host=args.host, post=args.post)
    except Exception as err:
        print(err, file=sys.stderr)
