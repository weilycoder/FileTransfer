from app import *
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch the File Transfer, which defaults to starting in client mode.")
    parser.add_argument(
        "-s", "--server", help="start in server mode", action="store_true"
    )
    parser.add_argument(
        "--superpasswd",
        help="set a super password, only effective when starting in server mode",
    )
    args = parser.parse_args()
    if args.server:
        app = Server(super_passwd=args.superpasswd)
        app.start()
        wait()
    else:
        UI()
