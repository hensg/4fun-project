#!venv/bin/python3.6

import pathlib
import os
import json
import datetime
from random import random

os.makedirs('sample.jsonl/', exist_ok=True)

with open('sample.jsonl/afile', 'w') as f:
    for i in range(1, 5000):
        model1 = {
            'pk': 'item_{}'.format(str(i)),
            'score': str(random()),
            'buildDate': str(datetime.datetime.now().date() - datetime.timedelta(days=30)),
            'modelName': 'model1',
            'version': 'v1'
        }
        f.write(json.dumps(model1) + '\n')

    for i in range(1, 5000):
        model1 = {
            'pk': 'item_{}'.format(str(i)),
            'score': str(random()),
            'buildDate': str(datetime.datetime.now().date()),
            'modelName': 'model1',
            'version': 'v1'
        }
        f.write(json.dumps(model1) + '\n')

    for i in range(1, 5000):
        model2 = {
            'pk': 'item_{}'.format(i),
            'size': random(),
            'buildDate': str(datetime.datetime.now().date()),
            'modelName': 'model2',
            'version': 'v1'
        }
        f.write(json.dumps(model2) + '\n')

    for i in range(9):
        invalid = {
            'invalid schema': 'to raise error on API'
        }
        f.write(json.dumps(invalid) + '\n')
