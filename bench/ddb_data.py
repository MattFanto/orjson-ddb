# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from json import loads as json_loads

from orjson import loads as orjson_loads
from orjson_ddb import loads as orjson_ddb_loads
from dynamodb_json import json_util
from boto3.dynamodb.types import TypeDeserializer


def deserializer():
    # not implemented yet
    pass


def loads_ddb_boto3(obj, loader):
    d = loader(obj)
    type_des = TypeDeserializer()
    res = {}
    for k, v in d.items():
        res[k] = type_des.deserialize(v)
    return res


libraries = {
    "orjson-ddb": (deserializer, orjson_ddb_loads),
    "boto3-json": (deserializer, lambda x: loads_ddb_boto3(x, json_loads)),
    "boto3-orjson": (deserializer, lambda x: loads_ddb_boto3(x, orjson_loads)),
    "dynamodb-json-util": (deserializer, json_util.loads),
}

fixtures = [
    "canada.json",
    "citm_catalog.json",
    # this is a list so we can't test it
    # "github.json",
    "twitter.json",
]
