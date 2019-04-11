import happybase_mock as happybase
import pytest

from app.dao.model1 import Model1DAO
from app.models.model1 import Model1

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
        conn.create_table(Model1DAO.TABLE_NAME, {'score': dict()})
    return mock_db

def test_model1dao_put_and_get(mock_db_with_table_created):
    dao = Model1DAO(mock_db_with_table_created)
    key = 'a'
    model1 = Model1(key, score='99')

    dao.put(model1.pk, model1.to_hbase())
    row = dao.get(key)

    actually_model1 = Model1.from_hbase(key, row)
    assert actually_model1.pk == model1.pk
    assert actually_model1.score == model1.score

def test_model1dao_put_and_delete(mock_db_with_table_created):
    dao = Model1DAO(mock_db_with_table_created)
    key = 'a'
    model1 = Model1(key, score='99')

    dao.put(model1.pk, model1.to_hbase())
    row = dao.get(key)
    assert row != None
    
    dao.delete(key)
    row = dao.get(key)
    assert row == {}

def test_model1dao_scan(mock_db_with_table_created):
    dao = Model1DAO(mock_db_with_table_created)
    model1s = [
        Model1(str(i), score=str(i))
        for i in range(200)
    ]
    for m in model1s:
        dao.put(m.pk, m.to_hbase())

    scanned = dao.scan()
    assert len(list(scanned)) == 200
