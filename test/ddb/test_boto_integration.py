import contextlib
from decimal import Decimal

import pytest
from moto import mock_dynamodb2
import boto3
from botocore.parsers import PROTOCOL_PARSERS
import orjson_ddb


@contextlib.contextmanager
def json_ddb_parser():
    # Start the timer
    _parser = PROTOCOL_PARSERS.get("json")
    old_parser = getattr(_parser, "_handle_json_body")

    def new_parser(self, raw_body, shape):
        return orjson_ddb.loads(raw_body)

    setattr(_parser, "_handle_json_body", new_parser)

    yield

    setattr(_parser, "_handle_json_body", old_parser)


TABLE_NAME = "some_table"

ITEM = {
    'pk': 'pk1',
    'sk': 'sk1',
    'vector': [1.0] * 512
}

@pytest.fixture
def dynamodb_mocked():
    mocked_dynamodb = mock_dynamodb2()
    mocked_dynamodb.start()
    yield None
    mocked_dynamodb.stop()


@pytest.fixture
def dynamo_table(dynamodb_mocked):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    dynamodb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
            # {'AttributeName': 'payload', 'AttributeType': 'S'},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )


@pytest.fixture
def put_item_in_ddb(dynamodb_mocked):
    table = boto3.resource('dynamodb', region_name='us-east-1').Table(TABLE_NAME)
    item = ITEM.copy()
    item["vector"] = [Decimal(str(x)) for x in ITEM["vector"]]
    table.put_item(Item=item)
    item = item.copy()
    item["pk"] = "pk2"
    table.put_item(Item=item)


def test_ddb_boto3_get_item(dynamodb_mocked, dynamo_table, put_item_in_ddb):
    dynamodb_client = boto3.client("dynamodb", region_name="us-east-1")
    with json_ddb_parser():
        resp = dynamodb_client.get_item(
            TableName=TABLE_NAME,
            Key={"pk": {"S": "pk1"}, "sk": {"S": "sk1"}}
        )
        assert resp["Item"] == ITEM
        assert "ResponseMetadata" in resp


def test_ddb_boto3_query_items(dynamodb_mocked, dynamo_table, put_item_in_ddb):
    dynamodb_client = boto3.client("dynamodb", region_name="us-east-1")
    with json_ddb_parser():
        resp = dynamodb_client.query(
            TableName=TABLE_NAME,
            KeyConditionExpression='pk = :pk',
            ExpressionAttributeValues={
                ':pk': {'S': 'pk1'}
            }
        )
        assert resp["Items"][0] == ITEM
        assert len(resp["Items"]) == 1
        assert resp["Count"] == 1
        assert resp["ScannedCount"] == 2
        assert "ResponseMetadata" in resp
