# API

An API written in Python 3.6 using falcon framework,
The API receives JSON (`api/app/schemas/model1.json`),
validate it and save into HBase.

### Setup instructions

Setup virtual env

    make setup-venv

Running api
  
    make run-api

Running tests
  
    make test

### Usage instructions

API status
    
    curl localhost:8000/

Get/Scan collection (lexicographically sorted)
    
    curl localhost:8000/v1/model1?row_start=item_1&row_stop=item_2

Post collection

    curl -XPOST localhost:8000/v1/model1 -H 'Content-type: application/json' -d '{"pk": "item_1", "score": "0.2", "modelName": "model1", "version": "v1"}'

Get item
    
    curl localhost:8000/v1/model1/item_1

Put item

    curl -XPUT localhost:8000/v1/model1/item_1 -d '{"pk": "item_1", "score": "0.2", "modelName": "model1", "version": "v1"}' -H 'Content-Type: application/json'


Prometheus metrics
    
    curl localhost:8000/metrics
