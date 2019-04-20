import falcon
from falcon.media.validators import jsonschema
import jsonschema as jsc
import json

class SchemaValidator:

    def __init__(self):
        self.schema_dict = {}

    def validate(self, json_data, version, model_name): 
        if not 'pk' in json_data.keys():
            raise falcon.HTTPBadRequest('Failed data validation',
                    description='"pk" is a required property for all models')
        if not 'modelName' in json_data.keys():
            raise falcon.HTTPBadRequest('Failed data validation',
                    description='"modelName" is a required property for all models')
        try:
            schema = self.schema_dict.get(model_name)
            if not schema:
                schema_path = 'api/schemas/{}/{}.json'.format(version,model_name)
                schema = json.loads(open(schema_path).read())
                # could be loaded from external directory/file
                self.schema_dict[model_name] = schema

            jsc.validate(json_data, schema, format_checker=jsc.FormatChecker())

        except FileNotFoundError as e:
            raise falcon.HTTPBadRequest('Missing schema!',
                    'There is no schema for model: "{}/{}".'.format(version, model_name))

        except jsc.ValidationError as e:
            raise falcon.HTTPBadRequest('Failed data validation', description=e.message)

        except jsc.exceptions.SchemaError as e:
            raise falcon.HTTPInternalServerError(
                    'Schema is invalid for model {}/{}!'.format(version, model_name),
                    description=e.message)
