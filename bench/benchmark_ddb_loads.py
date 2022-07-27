# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from json import loads as json_loads

import pytest

from .data import ddb_fixtures, ddb_libraries
from .util import read_fixture


@pytest.mark.parametrize("fixture", ddb_fixtures)
@pytest.mark.parametrize("library", ddb_libraries)
def test_loads(benchmark, fixture, library):
    lib = ddb_libraries[library]
    dumper = lib[0]
    loader = lib[1]
    benchmark.group = f"{fixture} deserialization"
    benchmark.extra_info["lib"] = library
    data = read_fixture(f"{fixture}.xz")
    if len(lib) == 3:
        data = lib[2](data)
    benchmark.extra_info["correct"] = json_loads(dumper(loader(data))) == json_loads(
        data
    )
    benchmark(loader, data)
    print(loader(data))
