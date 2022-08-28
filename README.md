# orjson-ddb

orjson-ddb is a fast DynamoDB native JSON library for Python. 
It is a fork/reboot of [orjson](https://github.com/ijl/orjson) (from which it inherits the [fast performance](https://github.com/ijl/orjson#performance)) 
adapted to serialize and deserialize DDB native JSON format in Python.
Compared to the classic [boto3](https://github.com/boto/boto3) DynamoDB [TypeDeserializer](https://github.com/boto/boto3/blob/1.24.61/boto3/dynamodb/types.py#L82), it deserializes DynamoDB response 40x faster.

orjson-ddb supports CPython 3.7, 3.8, 3.9, 3.10, and 3.11. It distributes x86_64/amd64,
aarch64/armv8, and arm7 wheels for Linux, amd64 and aarch64 wheels for macOS,
and amd64 wheels for Windows. orjson does not support PyPy. Releases
follow semantic versioning and serializing a new object type
without an opt-in flag is considered a breaking change.

orjson is licensed under both the Apache 2.0 and MIT licenses. The
repository and issue tracker is
[github.com/ijl/orjson](https://github.com/ijl/orjson), and patches may be
submitted there. There is a
[CHANGELOG](https://github.com/ijl/orjson/blob/master/CHANGELOG.md)
available in the repository.

1. [Usage](https://github.com/ijl/orjson#usage)
    1. [Install](https://github.com/ijl/orjson#install)
    2. [Quickstart](https://github.com/ijl/orjson#quickstart)
    3. [Migrating](https://github.com/ijl/orjson#migrating)
    4. [Serialize](https://github.com/ijl/orjson#serialize)
        1. [default](https://github.com/ijl/orjson#default)
        2. [option](https://github.com/ijl/orjson#option)
    5. [Deserialize](https://github.com/ijl/orjson#deserialize)
2. [Types](https://github.com/ijl/orjson#types)
    1. [dataclass](https://github.com/ijl/orjson#dataclass)
    2. [datetime](https://github.com/ijl/orjson#datetime)
    3. [enum](https://github.com/ijl/orjson#enum)
    4. [float](https://github.com/ijl/orjson#float)
    5. [int](https://github.com/ijl/orjson#int)
    6. [numpy](https://github.com/ijl/orjson#numpy)
    7. [str](https://github.com/ijl/orjson#str)
    8. [uuid](https://github.com/ijl/orjson#uuid)
3. [Testing](https://github.com/ijl/orjson#testing)
4. [Performance](https://github.com/ijl/orjson#performance)
    1. [Latency](https://github.com/ijl/orjson#latency)
    2. [Memory](https://github.com/ijl/orjson#memory)
    3. [Reproducing](https://github.com/ijl/orjson#reproducing)
5. [Questions](https://github.com/ijl/orjson#questions)
6. [Packaging](https://github.com/ijl/orjson#packaging)
7. [License](https://github.com/ijl/orjson#license)

## Usage

### Install

To install a wheel from PyPI:

```sh
pip install --upgrade "pip>=20.3" # manylinux_x_y, universal2 wheel support
pip install --upgrade orjson
```

To build a wheel, see [packaging](https://github.com/ijl/orjson#packaging).

### Quickstart

This library exposes a function `loads` which can deserializer DynamoDB response into a Python dictionary.
This can be used to parse the API response from DynamoDB, as an example if you are using the REST API:
```python
import requests
import orjson_ddb

response = requests.post("https://dynamodb.us-east-1.amazonaws.com/", data={
   "TableName": "some_table", 
   "Key": {"pk": {"S": "pk1"}, "sk": {"S": "sk1"}}
}, headers={
   # some headers
})
data = orjson_ddb.loads(response.content)
```
The same results can be achieved when using boto3 via a context manager provided by the library:
```python
import boto3
from orjson_ddb import ddb_json_parser


dynamodb_client = boto3.client("dynamodb", region_name="us-east-1")
with ddb_json_parser():
   resp = dynamodb_client.get_item(
      TableName="some_table",
      Key={"pk": {"S": "pk1"}, "sk": {"S": "sk1"}}
   )
print(resp["Items"])
# {'sk': 'sk1', 'pk': 'pk1', 'data': {'some_number': 0.123, 'some_string': 'hello'}}
```
This context manager tells boto3 to use `orjson_ddb.loads` to deserialize the DynamoDB response.
The output dictionary doesn't contain any reference to the DynamoDB Native format and the result is the same of
what you would get with `boto3.resource('dynamodb').Table('some_table').get_item(Key={"pk": "pk1", "sk": "sk1"})["Item"]`
except for "N" type being translated directly to int or float instead of Decimal.

N.B. Unfortunately at the moment it is not possible to use the `boto3.resource`.


## Performance

Serialization and deserialization performance of orjson is better than
ultrajson, rapidjson, simplejson, or json. The benchmarks are done on
fixtures of real data:

* twitter.json, 631.5KiB, results of a search on Twitter for "一", containing
CJK strings, dictionaries of strings and arrays of dictionaries, indented.

* github.json, 55.8KiB, a GitHub activity feed, containing dictionaries of
strings and arrays of dictionaries, not indented.

* citm_catalog.json, 1.7MiB, concert data, containing nested dictionaries of
strings and arrays of integers, indented.

* canada.json, 2.2MiB, coordinates of the Canadian border in GeoJSON
format, containing floats and arrays, indented.

### Latency

#### twitter.json serialization

| Library    |   Median latency (milliseconds) |   Operations per second |   Relative (latency) |
|------------|---------------------------------|-------------------------|----------------------|
| orjson     |                            0.33 |                  3069.4 |                 1    |
| ujson      |                            1.68 |                   592.8 |                 5.15 |
| rapidjson  |                            1.12 |                   891   |                 3.45 |
| simplejson |                            2.29 |                   436.2 |                 7.03 |
| json       |                            1.8  |                   556.6 |                 5.52 |

#### twitter.json deserialization

| Library    |   Median latency (milliseconds) |   Operations per second |   Relative (latency) |
|------------|---------------------------------|-------------------------|----------------------|
| orjson     |                            0.81 |                  1237.6 |                 1    |
| ujson      |                            1.87 |                   533.9 |                 2.32 |
| rapidjson  |                            2.97 |                   335.8 |                 3.67 |
| simplejson |                            2.15 |                   463.8 |                 2.66 |
| json       |                            2.45 |                   408.2 |                 3.03 |

#### github.json serialization

| Library    |   Median latency (milliseconds) |   Operations per second |   Relative (latency) |
|------------|---------------------------------|-------------------------|----------------------|
| orjson     |                            0.03 |                 28817.3 |                 1    |
| ujson      |                            0.18 |                  5478.2 |                 5.26 |
| rapidjson  |                            0.1  |                  9686.4 |                 2.98 |
| simplejson |                            0.26 |                  3901.3 |                 7.39 |
| json       |                            0.18 |                  5437   |                 5.27 |

#### github.json deserialization

| Library    |   Median latency (milliseconds) |   Operations per second |   Relative (latency) |
|------------|---------------------------------|-------------------------|----------------------|
| orjson     |                            0.07 |                 15270   |                 1    |
| ujson      |                            0.19 |                  5374.8 |                 2.84 |
| rapidjson  |                            0.17 |                  5854.9 |                 2.59 |
| simplejson |                            0.15 |                  6707.4 |                 2.27 |
| json       |                            0.16 |                  6397.3 |                 2.39 |

#### citm_catalog.json serialization

| Library    |   Median latency (milliseconds) |   Operations per second |   Relative (latency) |
|------------|---------------------------------|-------------------------|----------------------|
| orjson     |                            0.58 |                  1722.5 |                 1    |
| ujson      |                            2.89 |                   345.6 |                 4.99 |
| rapidjson  |                            1.83 |                   546.4 |                 3.15 |
| simplejson |                           10.39 |                    95.9 |                17.89 |
| json       |                            3.93 |                   254.6 |                 6.77 |

#### citm_catalog.json deserialization

| Library    |   Median latency (milliseconds) |   Operations per second |   Relative (latency) |
|------------|---------------------------------|-------------------------|----------------------|
| orjson     |                            1.76 |                   569.2 |                 1    |
| ujson      |                            3.5  |                   284.3 |                 1.99 |
| rapidjson  |                            5.77 |                   173.2 |                 3.28 |
| simplejson |                            5.13 |                   194.7 |                 2.92 |
| json       |                            4.99 |                   200.5 |                 2.84 |

#### canada.json serialization

| Library    |   Median latency (milliseconds) |   Operations per second |   Relative (latency) |
|------------|---------------------------------|-------------------------|----------------------|
| orjson     |                            3.62 |                   276.3 |                 1    |
| ujson      |                           14.16 |                    70.6 |                 3.91 |
| rapidjson  |                           33.64 |                    29.7 |                 9.29 |
| simplejson |                           57.46 |                    17.4 |                15.88 |
| json       |                           35.7  |                    28   |                 9.86 |

#### canada.json deserialization

| Library    |   Median latency (milliseconds) |   Operations per second |   Relative (latency) |
|------------|---------------------------------|-------------------------|----------------------|
| orjson     |                            3.89 |                   256.6 |                 1    |
| ujson      |                            8.73 |                   114.3 |                 2.24 |
| rapidjson  |                           23.33 |                    42.8 |                 5.99 |
| simplejson |                           23.99 |                    41.7 |                 6.16 |
| json       |                           21.1  |                    47.4 |                 5.42 |

### Memory

orjson as of 3.7.0 has higher baseline memory usage than other libraries
due to a persistent buffer used for parsing. Incremental memory usage when
deserializing is similar to the standard library and other third-party
libraries.

This measures, in the first column, RSS after importing a library and reading
the fixture, and in the second column, increases in RSS after repeatedly
calling `loads()` on the fixture.

#### twitter.json

| Library    |   import, read() RSS (MiB) |   loads() increase in RSS (MiB) |
|------------|----------------------------|---------------------------------|
| orjson     |                       21.8 |                             2.8 |
| ujson      |                       14.3 |                             4.8 |
| rapidjson  |                       14.9 |                             4.6 |
| simplejson |                       13.4 |                             2.4 |
| json       |                       13.1 |                             2.3 |

#### github.json

| Library    |   import, read() RSS (MiB) |   loads() increase in RSS (MiB) |
|------------|----------------------------|---------------------------------|
| orjson     |                       21.2 |                             0.5 |
| ujson      |                       13.6 |                             0.6 |
| rapidjson  |                       14.1 |                             0.5 |
| simplejson |                       12.5 |                             0.3 |
| json       |                       12.4 |                             0.3 |

#### citm_catalog.json

| Library    |   import, read() RSS (MiB) |   loads() increase in RSS (MiB) |
|------------|----------------------------|---------------------------------|
| orjson     |                       23   |                            10.6 |
| ujson      |                       15.2 |                            11.2 |
| rapidjson  |                       15.8 |                            29.7 |
| simplejson |                       14.4 |                            24.7 |
| json       |                       13.9 |                            24.7 |

#### canada.json

| Library    |   import, read() RSS (MiB) |   loads() increase in RSS (MiB) |
|------------|----------------------------|---------------------------------|
| orjson     |                       23.2 |                            21.3 |
| ujson      |                       15.6 |                            19.2 |
| rapidjson  |                       16.3 |                            23.4 |
| simplejson |                       15   |                            21.1 |
| json       |                       14.3 |                            20.9 |

### Reproducing

The above was measured using Python 3.10.5 on Linux (amd64) with
orjson 3.7.9, ujson 5.4.0, python-rapidson 1.8, and simplejson 3.17.6.

The latency results can be reproduced using the `pybench` and `graph`
scripts. The memory results can be reproduced using the `pymem` script.

## Questions

### Why can't I install it from PyPI?

Probably `pip` needs to be upgraded to version 20.3 or later to support
the latest manylinux_x_y or universal2 wheel formats.

### "Cargo, the Rust package manager, is not installed or is not on PATH."

This happens when there are no binary wheels (like manylinux) for your
platform on PyPI. You can install [Rust](https://www.rust-lang.org/) through
`rustup` or a package manager and then it will compile.

### Will it deserialize to dataclasses, UUIDs, decimals, etc or support object_hook?

No. This requires a schema specifying what types are expected and how to
handle errors etc. This is addressed by data validation libraries a
level above this.

### Will it serialize to `str`?

No. `bytes` is the correct type for a serialized blob.

### Will it support PyPy?

Probably not.

## Packaging

To package orjson requires at least [Rust](https://www.rust-lang.org/) 1.57
and the [maturin](https://github.com/PyO3/maturin) build tool. The recommended
build command is:

```sh
maturin build --release --strip
```

It benefits from also having a C build environment to compile a faster
deserialization backend. See this project's `manylinux_2_28` builds for an
example using clang and LTO.

The project's own CI tests against `nightly-2022-07-26` and stable 1.54. It
is prudent to pin the nightly version because that channel can introduce
breaking changes.

orjson is tested for amd64, aarch64, and arm7 on Linux. It is tested for
amd64 on macOS and cross-compiles for aarch64. For Windows it is tested on
amd64.

There are no runtime dependencies other than libc.

orjson's tests are included in the source distribution on PyPI. The
requirements to run the tests are specified in `test/requirements.txt`. The
tests should be run as part of the build. It can be run with
`pytest -q test`.

## License

orjson was written by ijl <<ijl@mailbox.org>>, copyright 2018 - 2022, licensed
under both the Apache 2 and MIT licenses.
