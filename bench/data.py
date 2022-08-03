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
from boto3.dynamodb.types import TypeDeserializer


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


def loads_ddb(obj, loader):
    d = loader(obj)
    # return dynamodb_json_util.loads(d)
    d["vector"] = [float(x["N"]) for x in d["vector"]["L"]]
    d["pk"] = d["pk"]["S"]
    d["sk"] = d["sk"]["S"]
    return d


def loads_ddb_string(obj, loader):
    d = loader(obj)
    d["vector"] = loader(d["vector"]["S"])
    d["pk"] = d["pk"]["S"]
    d["sk"] = d["sk"]["S"]
    return d


def loads_ddb_string_pre(obj):
    import json
    d = json.loads(obj)
    d["vector"] = {"S": json.dumps([float(x["N"]) for x in d["vector"]["L"]])}
    return json.dumps(d).encode("utf-8")


def loads_ddb_boto3(obj, loader):
    d = loader(obj)
    deserializer = TypeDeserializer()
    d["vector"] = [
        float(deserializer.deserialize(x)) for x in
        d["vector"]["L"]
    ]
    d["pk"] = d["pk"]["S"]
    d["sk"] = d["sk"]["S"]
    return d


ddb_libraries = {
    "custom-ddb": (orjson_dumps, orjson_ddb_loads),
    # "orjson-ddb": (orjson_dumps, lambda x: loads_ddb(x, orjson_loads)),
    # "ujson-ddb": (orjson_dumps, lambda x: loads_ddb(x, ujson_loads)),
    # "json-dbb": (_json_dumps, lambda x: loads_ddb(x, json_loads)),
    "orjson-string": (orjson_dumps, lambda x: loads_ddb_string(x, orjson_loads), loads_ddb_string_pre),
    "ujson-string": (orjson_dumps, lambda x: loads_ddb_string(x, ujson_loads), loads_ddb_string_pre),
    "json-string": (_json_dumps, lambda x: loads_ddb_string(x, json_loads), loads_ddb_string_pre),
    # "boto3-json": (orjson_dumps, lambda x: loads_ddb_boto3(x, json_loads)),
    # "boto3-ujson": (orjson_dumps, lambda x: loads_ddb_boto3(x, ujson_loads)),
}

ddb_fixtures = [
    "ddb_vectors.json"
]
