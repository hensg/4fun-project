"""Job to send data to api"""
import datetime
import sys
import logging
import requests
import json
import time
from pyspark import SparkContext, SparkConf

conf = SparkConf().setAppName('putter')
sc = SparkContext(conf=conf)

success_acc = sc.accumulator(0)
failure_acc = sc.accumulator(0)

def get_logger():
    log = logging.getLogger(__file__)
    log.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log

def get_data_from_api(api_host_port, version, model_name, pk):
    get_endpoint = 'http://{}/{}/{}/{}'.format(api_host_port, version, model_name, pk)
    response = requests.get(get_endpoint)
    if response:
        return response.json()
    return None

def add_history_to_model(existing_item, line_json, version, model_name, pk, buildDate):
    if not existing_item:
        existing_item = {
            'modelName': model_name,
            'version': version,
            'pk': pk,
            'history': {}
        }

    values_without_metadata = {
        k:v for (k,v) in line_json.items()
        if k not in ['modelName', 'pk', 'version', 'buildDate']
    }# all other json data from model, maybe 1, maybe 40 properties

    existing_item['history'][buildDate] = values_without_metadata
    return existing_item

def save_in_api(line, attempt=1):
    global success_acc, failure_acc
    line_json = json.loads(line)

    pk = line_json.get('pk', None)
    model_name = line_json.get('modelName', None)
    version = line_json.get('version', None)
    buildDate = line_json.get('buildDate', None)

    try:
        existing_item = get_data_from_api(api_host_port, version, model_name, pk)
        item_to_update_with_history = add_history_to_model(existing_item, line_json, version, model_name, pk, buildDate)

        endpoint = 'http://{}/{}/{}/{}'.format(api_host_port, version, model_name, pk)
        headers = {'Content-Type': 'application/json'}
        response = requests.put(endpoint, headers=headers, json=item_to_update_with_history)

        if response:
            success_acc += 1
        elif response.status_code == 503 and attempt <= 3:
            # hold for some seconds and retry
            time.sleep(3**attempt)
            return save_in_api(line, attempt=attempt+1)
        else:
            failure_acc += 1
            return {'success': False, 'http_status': response.status_code, 'line': line, 'err': response.text}

    except requests.exceptions.ConnectionError as e:
        return {'success': False, 'line': line, 'err': 'Failed to connect to API'}

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise 'Missing args! Type <host:port> <path>'
    
    api_host_port, path = sys.argv[1:]
    job_datetime_str = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')
    
    log = get_logger()
    log.info('Starting to process path: {}, to send to {}'.format(path, api_host_port))
    jsonlines_rdd = sc.textFile(path)
    
    if jsonlines_rdd.isEmpty():
        log.info('There is no text file in path: {}'.format(path))
        sys.exit(0)

    to_save = jsonlines_rdd.map(save_in_api).filter(lambda x: x != None)

    faileds = to_save.filter(lambda x: not x['success'])
    faileds.map(json.dumps).saveAsTextFile('/joboutput/{}/failed.json'.format(job_datetime_str))
    
    log.info('Sent {} lines with success!'.format(success_acc.value))
    log.info('Failed to post {} lines'.format(failure_acc.value))
