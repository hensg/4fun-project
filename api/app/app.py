"""Main API module"""
import falcon
from falcon_prometheus import PrometheusMiddleware
from thriftpy.transport import TTransportException
import app.dao.model1
import app.resources.model1
import app.resources.status
from app.dao.db_manager import DBManager
from app.handlers.thrift_exception_handler import ThriftExpcetionHandler

def create_app(db_manager):
    """Create falcon API"""
    model1dao = app.dao.model1.Model1DAO(db_manager)

    prometheus = PrometheusMiddleware()
    api = falcon.API(
        middleware=[
            prometheus
        ]
    )
    api.add_route('/', app.resources.status.Status(db_manager))
    api.add_route('/model1s', app.resources.model1.Collection(model1dao))
    api.add_route('/model1s/{key}', app.resources.model1.Item(model1dao))
    api.add_route('/metrics', prometheus)

    api.add_error_handler(TTransportException,
                          ThriftExpcetionHandler(db_manager).thrift_ex_handler)
    return api

def get_app():
    db_manager = DBManager(host='hbase-docker')
    return create_app(db_manager)
