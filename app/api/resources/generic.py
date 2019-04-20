import logging
import falcon
import json
from api.models.generic import Generic
from api.resources.schema_validator import SchemaValidator

class Collection:

    def __init__(self, dao):
        self.dao = dao
        self.schema_validator = SchemaValidator()

    def on_get(self, req, resp, version, model_name):
        """Get from data using pagination"""

        logging.debug('on_get collection scanning') 

        row_start = req.params.get('row_start')
        row_stop = req.params.get('row_stop')
        if not row_start or not row_stop:
            raise falcon.HTTPBadRequest(
            description='Missing row_start({}) and/or row_stop({}) query params!'.format(row_start, row_stop))

        scanned_data = self.dao.scan(model_name, version, row_start, row_stop, limit=100)

        if scanned_data:
            rows = [
                Generic.from_hbase(k, v).to_dict()
                for (k, v) in scanned_data
            ]
            resp.media = rows
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404

    def on_post(self, req, resp, version, model_name):
        self.schema_validator.validate(req.media, version, model_name)
        if req.media['version'] != version:
            raise falcon.HTTPBadRequest('Bad request',
                    'Resource version is not equal to version from body!')
        if req.media['modelName'] != model_name:
            raise falcon.HTTPBadRequest('Bad request',
                    'Resource model name is not equal to model name from body!')

        model = Generic.from_json(req.media)

        logging.debug('on_post collection with key: {}', model.pk)
        if self.dao.get(model_name, version, model.pk):
            resp.status = falcon.HTTP_409
            resp.media = {
                'err': 'Model with pk ({}) already exists, use PUT to update!'.format(model.pk)
            }
        else:
            self.dao.put(model_name,  version, model.pk, model.to_hbase())
            resp.status = falcon.HTTP_201
            resp.location = '{}/{}/{}'.format(version, model_name, model.pk)

class Item:

    def __init__(self, dao):
        self.dao = dao
        self.schema_validator = SchemaValidator()

    def on_get(self, req, resp, version, model_name, key):
        logging.debug('on_get item with key: {}'.format(key))
        row = self.dao.get(model_name, version, key)
        if row:
            resp.body = Generic.from_hbase(key, row).to_json()
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404

    def on_put(self, req, resp, version, model_name, key):
        self.schema_validator.validate(req.media, version, model_name)
        if req.media['pk'] != key:
            raise falcon.HTTPBadRequest('Bad request',
                    'Resource pk is not equal to pk from body!')
        if req.media['version'] != version:
            raise falcon.HTTPBadRequest('Bad request',
                    'Resource version is not equal to version from body!')
        if req.media['modelName'] != model_name:
            raise falcon.HTTPBadRequest('Bad request',
                    'Resource model name is not equal to model name from body!')

        model = Generic.from_json(req.media)
        logging.debug('on_put item with key: {}'.format(model.pk))
        self.dao.put(model_name, version, key, model.to_hbase())
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp, version, model_name, key):
        logging.debug('on_delete item with key: {}'.format(key))
        self.dao.delete(model_name, version, key)
        resp.status = falcon.HTTP_204
