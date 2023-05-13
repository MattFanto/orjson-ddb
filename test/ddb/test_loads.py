import pytest
import orjson_ddb


def test_orjson_ddb_loads_number():
    input_data = b'{"pk": {"N": "123"}}'
    expected_output = {"pk": 123}
    output_data = orjson_ddb.loads(input_data)
    assert output_data == expected_output


def test_orjson_ddb_loads_boolean():
    input_data = b'{"is_true": {"BOOL": true}}'
    expected_output = {"is_true": True}
    output_data = orjson_ddb.loads(input_data)
    assert output_data == expected_output


def test_orjson_ddb_loads_null():
    input_data = b'{"is_null": {"NULL": true}}'
    expected_output = {"is_null": None}
    output_data = orjson_ddb.loads(input_data)
    assert output_data == expected_output


def test_orjson_ddb_loads_list():
    input_data = b'{"list": {"L": [{"S": "item1"}, {"S": "item2"}]}}'
    expected_output = {"list": ["item1", "item2"]}
    output_data = orjson_ddb.loads(input_data)
    assert output_data == expected_output


def test_orjson_ddb_loads_map():
    input_data = b'{"map": {"M": {"key1": {"S": "value1"}, "key2": {"N": "123"}}}}'
    expected_output = {"map": {"key1": "value1", "key2": 123}}
    output_data = orjson_ddb.loads(input_data)
    assert output_data == expected_output
