"""Main API module"""
import falcon
from falcon_prometheus import PrometheusMiddleware
from thriftpy.transport import TTransportException
import app.dao.generic
import app.resources.generic
import app.resources.status
from app.dao.db_manager import DBManager
from app.handlers.thrift_exception import ThriftExpcetionHandler

def create_app(db_manager):
    """Create falcon API"""
    model_dao = app.dao.generic.GenericDAO(db_manager)

    prometheus = PrometheusMiddleware()
    api = falcon.API(
        middleware=[
            prometheus
        ]
    )
    api.add_route('/', app.resources.status.Status(db_manager))
    api.add_route('/{model_name}', app.resources.generic.Collection(model_dao))
    api.add_route('/{model_name}/{key}', app.resources.generic.Item(model_dao))
    api.add_route('/metrics', prometheus)

    api.add_error_handler(TTransportException,
                          ThriftExpcetionHandler(db_manager).thrift_ex_handler)
    return api

def get_app():
    db_manager = DBManager(host='hbase-docker')
    return create_app(db_manager)
