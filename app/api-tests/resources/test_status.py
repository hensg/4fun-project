import happybase_mock as happybase
import falcon
from falcon import testing
import pytest
import json

import api.api

@pytest.fixture
def mock_db():
    class MockDB:
        def __init__(self):
            self.conn_pool = None
        def pool(self):
            if not self.conn_pool:
                self.conn_pool = happybase.ConnectionPool(host='localhost', size=100)
            return self.conn_pool
    return MockDB()

@pytest.fixture()
def client(mock_db):
    return testing.TestClient(api.api.create_app(mock_db))

def test_api_status_ok(client):
    result = client.simulate_get(path='/')
    assert result.status == falcon.HTTP_200
    assert result.json == {'hbase-on': True, 'api-on': True}
