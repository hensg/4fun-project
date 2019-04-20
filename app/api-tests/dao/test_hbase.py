import happybase_mock as happybase
import pytest

from api.dao.generic import GenericDAO
from api.models.generic import Generic

TABLE_NAME='models'
MODEL_NAME='model1'

@pytest.fixture
def mock_db_with_table_created():
    class MockDB:
        def __init__(self):
            self.conn_pool = None
        def pool(self):
            if not self.conn_pool:
                self.conn_pool = happybase.ConnectionPool(host='localhost', size=100)
            return self.conn_pool

    mock_db = MockDB()
    with mock_db.pool().connection() as conn:
        conn.create_table(TABLE_NAME, {'value': dict()})
    return mock_db

def test_model1dao_put_and_get(mock_db_with_table_created):
    dao = GenericDAO(mock_db_with_table_created)
    key = 'a'
    generic_model = Generic(key, {'score':'99'})

    dao.put(MODEL_NAME, 'v1', generic_model.pk, generic_model.to_hbase())
    row = dao.get(MODEL_NAME, 'v1', key)

    actually_model1 = Generic.from_hbase(key, row)
    assert actually_model1.pk == generic_model.pk
    assert actually_model1.values == generic_model.values

def test_model1dao_put_and_delete(mock_db_with_table_created):
    dao = GenericDAO(mock_db_with_table_created)
    key = 'a'
    generic_model = Generic(key, {'score':'99'})

    dao.put(MODEL_NAME, 'v1', generic_model.pk, generic_model.to_hbase())
    row = dao.get(MODEL_NAME, 'v1', key)
    assert row != None
    
    dao.delete(MODEL_NAME, 'v1', key)
    row = dao.get(MODEL_NAME, 'v1', key)
    assert row == {}

def test_model1dao_scan(mock_db_with_table_created):
    dao = GenericDAO(mock_db_with_table_created)
    rows = [
        Generic(chr(i), {'score':str(i)})
        for i in range(200)
    ]
    for r in rows:
        dao.put(MODEL_NAME, 'v1', r.pk, r.to_hbase())

    scanned = dao.scan(MODEL_NAME, 'v1', row_start='a', row_stop='c')
    assert len(list(scanned)) == 2
