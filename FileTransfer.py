from app.server import *

if __name__ == "__main__":
    try:
        Server().start()
        while True:
            ...
    except KeyboardInterrupt:
        pass
