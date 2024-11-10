try:
    from starter import build_parser, start
except ImportError:
    from .starter import build_parser, start

if __name__ == "__main__":
    start(build_parser())
