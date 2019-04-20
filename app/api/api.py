"""Main API module"""
import falcon
from falcon_prometheus import PrometheusMiddleware
from thriftpy.transport import TTransportException
import api.dao.generic
import api.resources.generic
import api.resources.status
from api.dao.db_manager import DBManager
from api.handlers.thrift_exception import ThriftExpcetionHandler

def create_app(db_manager):
    """Create falcon API"""
    model_dao = api.dao.generic.GenericDAO(db_manager)

    prometheus = PrometheusMiddleware()
    fapi = falcon.API(
        middleware=[
            prometheus
        ]
    )
    fapi.add_route('/', api.resources.status.Status(db_manager))
    fapi.add_route('/{version}/{model_name}', api.resources.generic.Collection(model_dao))
    fapi.add_route('/{version}/{model_name}/{key}', api.resources.generic.Item(model_dao))
    fapi.add_route('/metrics', prometheus)

    fapi.add_error_handler(TTransportException,
                          ThriftExpcetionHandler(db_manager).thrift_ex_handler)
    return fapi

def get_app():
    db_manager = DBManager(host='hbase-docker')
    return create_app(db_manager)
