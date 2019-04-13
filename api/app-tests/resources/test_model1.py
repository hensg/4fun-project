import happybase_mock as happybase
import falcon
from falcon import testing
import pytest
import json
import app.app
from app.dao.db_manager import DBManager
from app.dao.generic import GenericDAO
from app.models.generic import Generic

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
        conn.create_table('model1', {'value': dict()})
        conn.create_table('model2', {'value': dict()})
    return mock_db

@pytest.fixture()
def client(mock_db):
    return testing.TestClient(app.app.create_app(mock_db))

def test_get_collection_empty(client):
    result = client.simulate_get(path='/model1')
    assert result.status == falcon.HTTP_200
    assert result.text == ''

def test_get_collection_with_two_values(mock_db, client):
    with mock_db.pool().connection() as conn:
        conn.table('model1').put(b'a', {b'value:value': json.dumps({'a':'1'}).encode()})
        conn.table('model1').put(b'b', {b'value:value': json.dumps({'b':'2'}).encode()})
        conn.table('model2').put(b'c', {b'value:value': json.dumps({'c':'3'}).encode()})
        conn.table('model2').put(b'd', {b'value:value': json.dumps({'d':'4'}).encode()})

    result = client.simulate_get(path='/model1')
    assert result.json == [
        {'a': '1'},
        {'b': '2'}
    ]
    result = client.simulate_get(path='/model2')
    assert result.json == [
        {'c': '3'},
        {'d': '4'}
    ]

def test_get_collection_with_pagination(mock_db, client):
    with mock_db.pool().connection() as conn:
        conn.table('model1').put(b'a', {b'value:value': json.dumps({'a':'1'}).encode()})
        conn.table('model1').put(b'b', {b'value:value': json.dumps({'b':'2'}).encode()})
        conn.table('model1').put(b'c', {b'value:value': json.dumps({'c':'3'}).encode()})
        conn.table('model1').put(b'd', {b'value:value': json.dumps({'d':'4'}).encode()})
        conn.table('model1').put(b'e', {b'value:value': json.dumps({'e':'5'}).encode()})
        conn.table('model1').put(b'f', {b'value:value': json.dumps({'f':'6'}).encode()})
        conn.table('model1').put(b'g', {b'value:value': json.dumps({'g':'7'}).encode()})

    result = client.simulate_get(path='/model1', query_string='row_start=c&row_stop=e')
    assert result.json == [
        {'c':'3'},
        {'d':'4'}
    ]

def test_post_collection_success(client):
    body = {'pk': 'a', 'score': '0.9'}
    result = client.simulate_post(
            path='/model1',
            json=body)
    assert result.status == falcon.HTTP_201

def test_post_collection_without_body(client):
    body = None
    result = client.simulate_post(
            path='/model1',
            json=body)
    assert result.status == falcon.HTTP_400
    assert result.json == {
            'description':'Could not parse JSON body - Expecting value: line 1 column 1 (char 0)',
            'title':'Invalid JSON'}

def test_post_collection_with_wrong_schema(client):
    body = {'test':'test'}
    result = client.simulate_post(
            path='/model1',
            json=body)
    assert result.status == falcon.HTTP_400
    assert result.json == {'title': 'Failed data validation',
            'description': '"pk" is a required property for all models'}

def test_put_item_with_success(client):
    body = {'pk': 'a', 'score': '0.9'}
    result = client.simulate_put(
            path='/model1/a',
            json=body)
    assert result.status == falcon.HTTP_200

def test_put_item_with_wrong_body_pk(client):
    body = {'pk': 'xxxxxa', 'score': '0.9'}
    result = client.simulate_put(
            path='/model1/a',
            json=body)
    assert result.status == falcon.HTTP_400

def test_put_item_without_body(client):
    body = None
    result = client.simulate_put(
            path='/model1/a',
            json=body)
    assert result.status == falcon.HTTP_400
    assert result.json == {
            'description':'Could not parse JSON body - Expecting value: line 1 column 1 (char 0)',
            'title':'Invalid JSON'}

def test_put_item_with_invalid_json_schema(client):
    body = {'bla':'wololo'}
    result = client.simulate_put(
            path='/model1/a',
            json=body)
    assert result.status == falcon.HTTP_400
    assert result.json == {'title': 'Failed data validation',
            'description': '"pk" is a required property for all models'}

def test_get_item_with_success(mock_db, client):
    with mock_db.pool().connection() as conn:
        conn.table('model1').put(b'a', {b'value:value': json.dumps({'x':'y'}).encode()})

    result = client.simulate_get(path='/model1/a')

    assert result.status == falcon.HTTP_200
    assert result.json == {'x': 'y'}

def test_get_item_with_success2(mock_db, client):
    with mock_db.pool().connection() as conn:
        conn.table('model1').put(b'a', {b'value:value': json.dumps({'a':'b'}).encode()})

    result = client.simulate_get(path='/model1/a')

    assert result.status == falcon.HTTP_200
    assert result.json == {'a': 'b'}

def test_get_item_not_found(client):
    result = client.simulate_get(path='/model1/a')
    assert result.status == falcon.HTTP_404

def test_delete_item_with_success(mock_db, client):
    with mock_db.pool().connection() as conn:
        conn.table('model1').put(b'a', {b'value:value': json.dumps({'x':'y'}).encode()})

    result = client.simulate_delete(path='/model1/a')
    assert result.status == falcon.HTTP_204
