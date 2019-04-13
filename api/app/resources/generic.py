import logging
import falcon
from falcon.media.validators import jsonschema
import json
import jsonschema as jsc
from app.models.generic import Generic

class SchemaValidator:

    def __init__(self):
        self.schema_dict = {}

    def __get_schema(self, model_name):
        schema = self.schema_dict.get(model_name)
        if not schema:
            try:
                schema = json.loads(open('app/schemas/{}.json'.format(model_name)).read())
                self.schema_dict[model_name] = schema
            except FileNotFoundError:
                raise falcon.HTTPBadRequest('Missing schema!',
                        'Model schema doesn\'t exists in API, please create it!')
        return schema

    def validate(self, json, model_name): 
        if not 'pk' in json.keys():
            raise falcon.HTTPBadRequest('Failed data validation',
                    description='"pk" is a required property for all models')
        try:
            schema = self.__get_schema(model_name)
            jsc.validate(json, schema, format_checker=jsc.FormatChecker())
        except jsc.ValidationError as e:
            raise falcon.HTTPBadRequest('Failed data validation', description=e.message)


class Collection:

    def __init__(self, dao):
        self.dao = dao
        self.schema_validator = SchemaValidator()

    def on_get(self, req, resp, model_name):
        """Get from data using pagination"""

        logging.debug('on_get collection scanning') 

        row_start = req.params.get('row_start')
        row_stop = req.params.get('row_stop')

        scanned_data = self.dao.scan(model_name, row_start, row_stop, limit=100)

        if scanned_data:
            rows = [
                Generic.from_hbase(k, v).to_dict()
                for (k, v) in scanned_data
            ]
            resp.media = rows
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp, model_name):
        self.schema_validator.validate(req.media, model_name)

        model = Generic.from_json(req.media)

        logging.debug('on_post collection with key: {}', model.pk)
        if self.dao.get(model_name, model.pk):
            resp.status = falcon.HTTP_409
            resp.media = {
                'err': 'Model with pk ({}) already exists, use PUT to update!'.format(model.pk)
            }
        else:
            self.dao.put(model_name, model.pk, model.to_hbase())
            resp.status = falcon.HTTP_201
            resp.location = '/{}/{}'.format(model_name, model.pk)

class Item:

    def __init__(self, dao):
        self.dao = dao
        self.schema_validator = SchemaValidator()

    def on_get(self, req, resp, model_name, key):
        logging.debug('on_get item with key: {}'.format(key))
        row = self.dao.get(model_name, key)
        if row:
            resp.body = Generic.from_hbase(key, row).to_json()
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404

    def on_put(self, req, resp, model_name, key):
        self.schema_validator.validate(req.media, model_name)

        model = Generic.from_json(req.media)
        if model.pk != key:
            raise falcon.HTTPBadRequest('Bad request',
                    'Resource pk is not equal to pk from body!')
        logging.debug('on_put item with key: {}'.format(model.pk))
        self.dao.put(model_name, key, model.to_hbase())
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp, model_name, key):
        logging.debug('on_delete item with key: {}'.format(key))
        self.dao.delete(model_name, key)
        resp.status = falcon.HTTP_204
