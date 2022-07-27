# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from json import dumps as _json_dumps
from json import loads as json_loads

from rapidjson import dumps as _rapidjson_dumps
from rapidjson import loads as rapidjson_loads
from simplejson import dumps as _simplejson_dumps
from simplejson import loads as simplejson_loads
from ujson import dumps as _ujson_dumps
from ujson import loads as ujson_loads

from orjson import dumps as _orjson_dumps
from orjson import loads as orjson_loads
from orjson_ddb import loads as orjson_ddb_loads
from orjson_ddb import dumps as orjson_ddb_dumps
from dynamodb_json import json_util as dynamodb_json_util

# dumps wrappers that return UTF-8


def orjson_dumps(obj):
    return _orjson_dumps(obj)


def ujson_dumps(obj):
    return _ujson_dumps(obj).encode("utf-8")


def rapidjson_dumps(obj):
    return _rapidjson_dumps(obj).encode("utf-8")


def json_dumps(obj):
    return _json_dumps(obj).encode("utf-8")


def simplejson_dumps(obj):
    return _simplejson_dumps(obj).encode("utf-8")


# Add new libraries here (pair of UTF-8 dumper, loader)
libraries = {
    "orjson": (orjson_dumps, orjson_loads),
    "orjson_ddb": (orjson_ddb_dumps, orjson_ddb_loads),
    # "ujson": (ujson_dumps, ujson_loads),
    # "json": (json_dumps, json_loads),
    # "rapidjson": (rapidjson_dumps, rapidjson_loads),
    # "simplejson": (simplejson_dumps, simplejson_loads),
}

# Add new JSON files here (corresponding to ../data/*.json.xz)
fixtures = [
    "canada.json",
    # "citm_catalog.json",
    # "github.json",
    # "twitter.json",
]


def orjons_loads_ddb(obj):
    d = orjson_loads(obj)
    return dynamodb_json_util.loads(d)
    # d["vector"] = [float(x["N"]) for x in d["vector"]["L"]]
    # return d


def json_loads_ddb(obj):
    d = json_loads(obj)
    d["vector"] = json_loads(d["vector"]["L"])
    return d


def orjons_loads_ddb_string(obj):
    d = orjson_loads(obj)
    # d = dynamodb_json_util.loads(d)
    d["pk"] = d["pk"]["S"]
    d["sk"] = d["sk"]["S"]
    d["vector"] = orjson_loads(d["vector"]["L"])
    return d


def json_loads_ddb_pre(obj):
    import json
    d = json.loads(obj)
    d["vector"] = {"L": json.dumps([float(x["N"]) for x in d["vector"]["L"]])}
    return json.dumps(d).encode("utf-8")


ddb_libraries = {
    # "my-naive-ddb-json": (orjson_dumps, loads_ddb_naive),
    "my-ddb-json": (orjson_dumps, orjson_ddb_loads),
    "orjson": (orjson_dumps, orjons_loads_ddb),
    "orjson-string": (orjson_dumps, orjons_loads_ddb_string, json_loads_ddb_pre),
    "json-string": (_json_dumps, json_loads_ddb, json_loads_ddb_pre)
}

ddb_fixtures = [
    "ddb_vectors.json"
]
