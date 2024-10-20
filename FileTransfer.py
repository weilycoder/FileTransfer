from app.server import *

if __name__ == "__main__":
    try:
        app = Server(super_passwd="super")
        app.start()
        while True:
            ...
    except KeyboardInterrupt:
        pass
