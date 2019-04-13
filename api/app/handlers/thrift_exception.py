import falcon

class ThriftExpcetionHandler:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def thrift_ex_handler(self, ex, req, resp, params):
        self.db_manager.reset_pool()
        raise falcon.HTTPServiceUnavailable(
            description='Retry in a few moments, please',
            retry_after=2)
