import happybase_mock as happybase
import falcon
from falcon import testing
import pytest
import json

import app.app

from app.dao.db_manager import DBManager
from app.dao.model1 import Model1DAO
from app.models.model1 import Model1

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
        conn.create_table(Model1DAO.TABLE_NAME, {'score': dict()})
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
        conn.table(Model1DAO.TABLE_NAME).put(b'a', {b'score:score': b'0.9'})
        conn.table(Model1DAO.TABLE_NAME).put(b'b', {b'score:score': b'0.2'})

    result = client.simulate_get(path='/model1')
    assert result.json == [
        {'pk': 'a', 'score': '0.9'},
        {'pk': 'b', 'score': '0.2'}
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
            headers={
                'Content-Type': 'application/json'
            },
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
            'description': "'pk' is a required property"}

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

#def test_put_item_without_auth(client):
#    body = {'pk': 'xxxxxa', 'score': '0.9'}
#    result = client.simulate_put(
#            path='/model1/a',
#            json=body)
#    assert result.status == falcon.HTTP_401

def test_put_item_without_body(client):
    body = None
    result = client.simulate_put(
            path='/model1/a',
            headers={
                'Content-Type': 'application/json'
            },
            json=body)
    assert result.status == falcon.HTTP_400
    assert result.json == {
            'description':'Could not parse JSON body - Expecting value: line 1 column 1 (char 0)',
            'title':'Invalid JSON'}

def test_put_item_with_invalid_json_schema(client):
    body = {'bla':'wololo'}
    result = client.simulate_put(
            path='/model1/a',
            headers={
                'Content-Type': 'application/json'
            },
            json=body)
    assert result.status == falcon.HTTP_400
    assert result.json == {'title': 'Failed data validation',
            'description': "'pk' is a required property"}

def test_get_item_with_success(mock_db, client):
    with mock_db.pool().connection() as conn:
        conn.table(Model1DAO.TABLE_NAME).put(b'a', {b'score:score': b'0.9'})

    result = client.simulate_get(path='/model1/a')

    assert result.status == falcon.HTTP_200
    assert result.json == {'pk': 'a', 'score': '0.9'}

def test_get_item_not_found(client):
    result = client.simulate_get(path='/model1/a')
    assert result.status == falcon.HTTP_404

def test_delete_item_with_success(mock_db, client):
    with mock_db.pool().connection() as conn:
        conn.table(Model1DAO.TABLE_NAME).put(b'a', {b'score:score': b'0.9'})

    result = client.simulate_delete(path='/model1/a')
    assert result.status == falcon.HTTP_204
