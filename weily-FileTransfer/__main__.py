import sys
import argparse
import tomlkit.exceptions

try:
    from app import Server, UI, asyncio, stdloggers
except ImportError:
    from .app import Server, UI, asyncio, stdloggers

try:
    from settings import MODE_CHOICES, SERVER, CheckBigInt, get_setting, Settings
except ImportError:
    from .settings import MODE_CHOICES, SERVER, CheckBigInt, get_setting, Settings


TOML_FILE = "filetransfer.toml"


def get_path():
    return "/".join(sys.argv[0].replace("\\", "/").split("/")[0:-1])


def get_toml_file():
    return (get_path() or ".") + "/" + TOML_FILE


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
    try:
        args = Settings(get_setting(parser.parse_args(), get_toml_file()))
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
    except (AssertionError, tomlkit.exceptions.TOMLKitError) as err:
        stdloggers.warn_logger("TOML Error:", str(err))
    except OSError as err:
        stdloggers.warn_logger(str(err))
    except Exception as err:
        stdloggers.err_logger(err)
    except KeyboardInterrupt:
        print("^C", file=sys.stderr)
        sys.exit(0)
    finally:
        stdloggers.close()
