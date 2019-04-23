import happybase_mock as happybase
import falcon
from falcon import testing
import pytest
import json
import api.api
from api.dao.db_manager import DBManager
from api.dao.generic import GenericDAO
from api.models.generic import Generic

TABLE_NAME='models'

@pytest.fixture
def mock_db():
    class MockDB:
        def __init__(self, host):
            self.conn_pool = None
            self.host = host
        def pool(self):
            if not self.conn_pool:
                self.conn_pool = happybase.ConnectionPool(host=self.host, size=100)
            return self.conn_pool
    mock_db = MockDB('localhost')
    with mock_db.pool().connection() as conn:
        conn.create_table(TABLE_NAME, {'value': dict()})
    return mock_db

@pytest.fixture()
def client(mock_db):
    return testing.TestClient(api.api.create_app(mock_db))

def test_get_collection_empty(client):
    result = client.simulate_get(path='/v1/model1', query_string='row_start=a&row_stop=z')
    assert result.status == falcon.HTTP_404
    assert result.text == ''

def test_get_collection_with_two_values(mock_db, client):
    with mock_db.pool().connection() as conn:
        conn.table(TABLE_NAME).put(b'model1|v1|a', {b'value:value': json.dumps({'a':'1'}).encode()})
        conn.table(TABLE_NAME).put(b'model1|v1|b', {b'value:value': json.dumps({'b':'2'}).encode()})
        conn.table(TABLE_NAME).put(b'model2|v1|c', {b'value:value': json.dumps({'c':'3'}).encode()})
        conn.table(TABLE_NAME).put(b'model2|v1|d', {b'value:value': json.dumps({'d':'4'}).encode()})

    result = client.simulate_get(path='/v1/model1', query_string='row_start=a&row_stop=c')
    assert result.json == [
        {'a': '1'},
        {'b': '2'}
    ]
    result = client.simulate_get(path='/v1/model2', query_string='row_start=c&row_stop=e')
    assert result.json == [
        {'c': '3'},
        {'d': '4'}
    ]

def test_get_collection_with_pagination(mock_db, client):
    with mock_db.pool().connection() as conn:
        conn.table(TABLE_NAME).put(b'model1|v1|a', {b'value:value': json.dumps({'a':'1'}).encode()})
        conn.table(TABLE_NAME).put(b'model1|v1|b', {b'value:value': json.dumps({'b':'2'}).encode()})
        conn.table(TABLE_NAME).put(b'model1|v1|c', {b'value:value': json.dumps({'c':'3'}).encode()})
        conn.table(TABLE_NAME).put(b'model1|v1|d', {b'value:value': json.dumps({'d':'4'}).encode()})
        conn.table(TABLE_NAME).put(b'model1|v1|e', {b'value:value': json.dumps({'e':'5'}).encode()})
        conn.table(TABLE_NAME).put(b'model1|v1|f', {b'value:value': json.dumps({'f':'6'}).encode()})
        conn.table(TABLE_NAME).put(b'model1|v1|g', {b'value:value': json.dumps({'g':'7'}).encode()})

    result = client.simulate_get(path='/v1/model1', query_string='row_start=c&row_stop=e')
    assert result.json == [
        {'c':'3'},
        {'d':'4'}
    ]

def test_post_collection_success(client):
    body = {
        'pk': 'a',
        'modelName': 'model1',
        'version': 'v1',
        'history': {
            '2018-01-01': {
                'score': '9'
            },
            '2018-02-01': {
                'score': 'A+'
            },
            '2018-03-01': {
                'score': 'B-'
            }
        }
    }
    result = client.simulate_post(
            path='/v1/model1',
            json=body)
    assert result.status == falcon.HTTP_201

def test_post_collection_without_body(client):
    body = None
    result = client.simulate_post(
            path='/v1/model1',
            json=body)
    assert result.status == falcon.HTTP_400
    assert result.json == {
            'description':'Could not parse JSON body - Expecting value: line 1 column 1 (char 0)',
            'title':'Invalid JSON'}

def test_post_collection_with_wrong_schema(client):
    body = {'test':'test'}
    result = client.simulate_post(
            path='/v1/model1',
            json=body)
    assert result.status == falcon.HTTP_400

def test_put_item_with_success(client):
    body = {
        'pk': 'a',
        'modelName': 'model2',
        'version': 'v1',
        'history': {
            '2019-01-01': {
                'size': 'AAA'
            },
            '2019-02-01': {
                'size': 'AAALarge'
            }
        }
    }
    result = client.simulate_put(
            path='/v1/model2/a',
            json=body)
    assert result.status == falcon.HTTP_200

def test_put_item_with_wrong_version(client):
    body = {
        'pk': 'a',
        'size': 9,
        'modelName': 'model2',
        'version': 'v3'
    }
    result = client.simulate_put(
            path='/v1/model2/a',
            json=body)
    assert result.status == falcon.HTTP_400

def test_put_item_with_wrong_body_pk(client):
    body = {
        'pk': 'xxxxxa',
        'score': '0.9',
        'modelName': 'model1',
        'version': 'v1'
    }
    result = client.simulate_put(
            path='/v1/model1/a',
            json=body)
    assert result.status == falcon.HTTP_400

def test_put_item_without_body(client):
    body = None
    result = client.simulate_put(
            path='/v1/model1/a',
            json=body)
    assert result.status == falcon.HTTP_400
    assert result.json == {
            'description':'Could not parse JSON body - Expecting value: line 1 column 1 (char 0)',
            'title':'Invalid JSON'}

def test_put_item_with_invalid_json_schema(client):
    body = {'bla':'wololo'}
    result = client.simulate_put(
            path='/v1/model1/a',
            json=body)
    assert result.status == falcon.HTTP_400

def test_get_item_with_success(mock_db, client):
    with mock_db.pool().connection() as conn:
        conn.table(TABLE_NAME).put(b'model1|v1|a', {b'value:value': json.dumps({'x':'y'}).encode()})

    result = client.simulate_get(path='/v1/model1/a')

    assert result.status == falcon.HTTP_200
    assert result.json == {'x': 'y'}

def test_get_item_with_success2(mock_db, client):
    with mock_db.pool().connection() as conn:
        conn.table(TABLE_NAME).put(b'model1|v1|a', {b'value:value': json.dumps({'a':'b'}).encode()})

    result = client.simulate_get(path='/v1/model1/a')

    assert result.status == falcon.HTTP_200
    assert result.json == {'a': 'b'}

def test_get_item_not_found(client):
    result = client.simulate_get(path='/v1/model1/a')
    assert result.status == falcon.HTTP_404

def test_delete_item_with_success(mock_db, client):
    with mock_db.pool().connection() as conn:
        conn.table(TABLE_NAME).put(b'model1|v1|a', {b'value:value': json.dumps({'x':'y'}).encode()})

    result = client.simulate_delete(path='/v1/model1/a')
    assert result.status == falcon.HTTP_204
