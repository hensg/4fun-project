#!venv/bin/python3.6

import pathlib
import os
import json
from random import random

with open('sample.jsonl', 'w') as f:
    for i in range(1, 5000):
        model1 = {
            'pk': 'item_{}'.format(str(i)),
            'score': str(random()),
            'modelName': 'model1'
        }
        f.write(json.dumps(model1) + '\n')

    for i in range(1, 5000):
        model2 = {
            'pk': 'item_{}'.format(i),
            'size': random(),
            'modelName': 'model2'
        }
        f.write(json.dumps(model2) + '\n')

    for i in range(9):
        invalid = {
            'invalid schema': 'to raise error on API'
        }
        f.write(json.dumps(invalid) + '\n')
