# orjson-ddb

orjson-ddb is a fast DynamoDB native JSON library for Python. 
It is a fork/reboot of [orjson](https://github.com/ijl/orjson) (from which it inherits the [fast performance](https://github.com/ijl/orjson#performance)) 
adapted to serialize and deserialize DDB native JSON format in Python.
Compared to [boto3](https://github.com/boto/boto3) DynamoDB [TypeDeserializer](https://github.com/boto/boto3/blob/1.24.61/boto3/dynamodb/types.py#L82), 
it deserializes DynamoDB response 10x faster and deserialize float numbers (e.g. `{"N": "0.13"}`) to float instead of Decimal.

orjson-ddb supports CPython 3.7, 3.8, 3.9, 3.10, and 3.11. It distributes x86_64/amd64,
aarch64/armv8, and arm7 wheels for Linux, amd64 and aarch64 wheels for macOS,
and amd64 wheels for Windows. orjson-ddb does not support PyPy. Releases
follow semantic versioning and serializing a new object type
without an opt-in flag is considered a breaking change.

The repository and issue tracker is [github.com/MattFanto/orjson-ddb](https://github.com/MattFanto/orjson-ddb), 
and patches may be submitted there. There is a [CHANGELOG](https://github.com/MattFanto/orjson-ddb/blob/master/CHANGELOG.md)
available in the repository.

1. [Usage](https://github.com/MattFanto/orjson-ddb#usage)
    1. [Install](https://github.com/MattFanto/orjson-ddb#install)
    2. [Quickstart](https://github.com/MattFanto/orjson-ddb#quickstart)
    3. [Deserialize](https://github.com/MattFanto/orjson-ddb#deserialize)
    4. [Serialize](https://github.com/MattFanto/orjson-ddb#serialize)
2. [Testing](https://github.com/MattFanto/orjson-ddb#testing)
3. [Performance](https://github.com/MattFanto/orjson-ddb#performance)
    1. [Latency](https://github.com/MattFanto/orjson-ddb#latency)
    2. [Memory](https://github.com/MattFanto/orjson-ddb#memory)
    3. [Reproducing](https://github.com/MattFanto/orjson-ddb#reproducing)
4. [Questions](https://github.com/MattFanto/orjson-ddb#questions)
5. [Packaging](https://github.com/MattFanto/orjson-ddb#packaging)
6. [License](https://github.com/MattFanto/orjson-ddb#license)

## Usage

### Install

To install a wheel from PyPI:

```sh
pip install --upgrade "pip>=20.3" # manylinux_x_y, universal2 wheel support
pip install --upgrade orjson-ddb
```

To build a wheel, see [packaging](https://github.com/MattFanto/orjson-ddb#packaging).

### Deserialize

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


### Serialize

Serialization of python dictionary to DynamoDB Native JSON format is not available yet.


## Performance

Deserialization performance of orjson-ddb is better than
boto3, dynamodb-json-util. The benchmarks are done on
fixtures of real data converted to DynamoDB native format:

* twitter.json, 631.5KiB, results of a search on Twitter for "一", containing
CJK strings, dictionaries of strings and arrays of dictionaries, indented.

* github.json, 55.8KiB, a GitHub activity feed, containing dictionaries of
strings and arrays of dictionaries, not indented.

* citm_catalog.json, 1.7MiB, concert data, containing nested dictionaries of
strings and arrays of integers, indented.

* canada.json, 2.2MiB, coordinates of the Canadian border in GeoJSON
format, containing floats and arrays, indented.

### Latency

#### twitter.json deserialization

| Library            |   Median latency (milliseconds) |   Operations per second |   Relative (latency) |
|--------------------|---------------------------------|-------------------------|----------------------|
| orjson-ddb         |                            2.17 |                   459.7 |                 1    |
| boto3-json         |                           18.61 |                    54.1 |                 8.57 |
| dynamodb-json-util |                           54.13 |                    18.4 |                24.92 |

#### citm_catalog.json deserialization

| Library            |   Median latency (milliseconds) |   Operations per second |   Relative (latency) |
|--------------------|---------------------------------|-------------------------|----------------------|
| orjson-ddb         |                            4.43 |                   240.3 |                 1    |
| boto3-json         |                           53.3  |                    18.6 |                12.03 |
| dynamodb-json-util |                           57.27 |                    17.5 |                12.93 |

#### canada.json deserialization

| Library            |   Median latency (milliseconds) |   Operations per second |   Relative (latency) |
|--------------------|---------------------------------|-------------------------|----------------------|
| orjson-ddb         |                           19.22 |                    52   |                 1    |
| boto3-json         |                          221.83 |                     4.5 |                11.54 |
| dynamodb-json-util |                          244.14 |                     4.1 |                12.7  |


### Reproducing

The above was measured using Python 3.9.13 on Linux (amd64) with
orjson-ddb 0.1.1, boto3==1.21.27, dynamodb-json==1.3

The latency results can be reproduced using the `pybench` and `graph`
scripts.

## Questions

### Why can't I install it from PyPI?

Probably `pip` needs to be upgraded to version 20.3 or later to support
the latest manylinux_x_y or universal2 wheel formats.

### "Cargo, the Rust package manager, is not installed or is not on PATH."

This happens when there are no binary wheels (like manylinux) for your
platform on PyPI. You can install [Rust](https://www.rust-lang.org/) through
`rustup` or a package manager and then it will compile.

### Will it support PyPy?

Probably not.

## Packaging

To package orjson-ddb requires at least [Rust](https://www.rust-lang.org/) 1.57
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

orjson-ddb is tested for amd64, aarch64, and arm7 on Linux. It is tested for
amd64 on macOS and cross-compiles for aarch64. For Windows it is tested on
amd64.

There are no runtime dependencies other than libc.

Tests are included in the source distribution on PyPI. The
requirements to run the tests are specified in `test/requirements.txt`. The
tests should be run as part of the build. It can be run with
`pytest -q test`.

## License

orjson was written by ijl <ijl@mailbox.org>, copyright 2018 - 2021, licensed under both the Apache 2 and MIT licenses.

orjson-ddb was forked from orjson and is maintained by Mattia Fantoni <mattia.fantoni@gmail.com>, licensed same as orjson.
