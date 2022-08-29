from .orjson_ddb import (
    __version__, dumps, loads, JSONDecodeError, JSONEncodeError,
    OPT_APPEND_NEWLINE,
    OPT_INDENT_2,
    OPT_NAIVE_UTC,
    OPT_NON_STR_KEYS,
    OPT_OMIT_MICROSECONDS,
    OPT_PASSTHROUGH_DATACLASS,
    OPT_PASSTHROUGH_DATETIME,
    OPT_PASSTHROUGH_SUBCLASS,
    OPT_SERIALIZE_DATACLASS,
    OPT_SERIALIZE_NUMPY,
    OPT_SERIALIZE_UUID,
    OPT_SORT_KEYS,
    OPT_STRICT_INTEGER,
    OPT_UTC_Z,
)
from .boto_integration import ddb_json_parser
