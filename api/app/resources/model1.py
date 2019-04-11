import logging
import falcon
from falcon.media.validators import jsonschema
import json
import jsonschema as jsc
from app.models.model1 import Model1

MODEL1_SCHEMA = json.loads(open('app/schemas/model1.json').read())

class Collection:

    def __init__(self, dao):
        self.dao = dao

    def on_get(self, req, resp):
        """Get from data using pagination"""

        logging.debug('on_get collection scanning') 

        row_start = req.params.get('row_start')
        row_stop = req.params.get('row_stop')

        scanned_data = self.dao.scan(row_start, row_stop, limit=100)

        if scanned_data:
            model1s = [
                Model1.from_hbase(k, v).to_dict()
                for (k, v) in scanned_data
            ]
            resp.media = model1s
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_200

    @jsonschema.validate(MODEL1_SCHEMA)
    def on_post(self, req, resp):
        payload = req.media
        model1 = Model1.from_json(payload)

        logging.debug('on_post collection with key: {}', model1.pk)
        self.dao.put(model1.pk, model1.to_hbase())

        resp.status = falcon.HTTP_201
        resp.location = '/model1/{}'.format(model1.pk)

class Item:

    def __init__(self, dao):
        self.dao = dao

    def on_get(self, req, resp, key):
        logging.debug('on_get item with key: {}'.format(key))
        row = self.dao.get(key)
        if row:
            resp.body = Model1.from_hbase(key, row).to_json()
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404

    @jsonschema.validate(MODEL1_SCHEMA)
    def on_put(self, req, resp, key):
        payload = req.media
        model1 = Model1.from_json(payload)
        if model1.pk != key:
            raise falcon.HTTPBadRequest('Bad request',
                    'Resource pk is not equal to pk from body!')
        logging.debug('on_put item with key: {}'.format(key))
        self.dao.put(key, model1.to_hbase())
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp, key):
        logging.debug('on_delete item with key: {}'.format(key))
        self.dao.delete(key)
        resp.status = falcon.HTTP_204
