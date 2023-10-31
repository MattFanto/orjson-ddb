import contextlib

try:
    from botocore.parsers import PROTOCOL_PARSERS
except ImportError as e:
    PROTOCOL_PARSERS = None
from .orjson_ddb import loads


@contextlib.contextmanager
def ddb_json_parser():
    if PROTOCOL_PARSERS is None:
        raise RuntimeError("Module 'botocore' needs to be installed")
    _parser = PROTOCOL_PARSERS.get("json")
    old_parser = getattr(_parser, "_handle_json_body")

    def new_parser(self, raw_body, shape):
        return loads(raw_body)

    setattr(_parser, "_handle_json_body", new_parser)

    yield

    setattr(_parser, "_handle_json_body", old_parser)
