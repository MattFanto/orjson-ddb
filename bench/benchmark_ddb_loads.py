# SPDX-License-Identifier: (Apache-2.0 OR MIT)
import json
from decimal import Decimal
from boto3.dynamodb.types import TypeSerializer

import pytest

from .ddb_data import fixtures, libraries
from .util import read_fixture


def convert_to_ddb(data):
    """
    Convert the fixture data to DynamoDB native format
    :param data:
    :return:
    """
    type_ser = TypeSerializer()
    res = {}
    # float are not supported https://github.com/boto/boto3/issues/665
    data = json.loads(data, parse_float=Decimal)
    for k, v in data.items():
        res[k] = type_ser.serialize(v)
    return json.dumps(res)


@pytest.mark.parametrize("fixture", fixtures)
@pytest.mark.parametrize("library", libraries)
def test_loads(benchmark, fixture, library):
    dumper, loader = libraries[library]
    benchmark.group = f"{fixture} deserialization"
    benchmark.extra_info["lib"] = library
    data = convert_to_ddb(read_fixture(f"{fixture}.xz"))
    benchmark(loader, data)
