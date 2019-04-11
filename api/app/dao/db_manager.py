import happybase
import app.dao.model1

class DBManager:

    def __init__(self, host, port=9090, pool_size=100):
        self.host = host
        self.port = port
        self.pool_size = 100
        self.conn_pool = None

    def pool(self):
        if self.conn_pool == None:
            self.conn_pool = happybase.ConnectionPool(host=self.host, port=self.port, size=self.pool_size)
        return self.conn_pool

    def reset_pool(self):
        self.conn_pool = None
