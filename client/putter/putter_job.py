"""Job to send data to api"""

import datetime
import sys
import logging
import requests
import json
import time
from pyspark import SparkContext, SparkConf

if len(sys.argv) <= 3:
    raise 'Missing arg! Type <host:port> <model> <path> to process files and send to host:port/model'

api_host_port, model, path = sys.argv[1], sys.argv[2], sys.argv[3]

def get_logger():
    log = logging.getLogger(__file__)
    log.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log

conf = SparkConf().setAppName('putter')
sc = SparkContext(conf=conf)

job_datetime_str = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')

log = get_logger()
log.info('Starting to process path: {}, to send to {}'.format(path, api_host_port))
jsonlines_rdd = sc.textFile(path)

if jsonlines_rdd.isEmpty():
    log.info('There is no text file in path: {}'.format(path))
    sys.exit(0)

def put_into_api(line, attempt=1):
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post('http://{}/{}'.format(api_host_port, model), headers=headers, data=line)
        if response:
            return {'success': True, 'http_status': response.status_code}

        elif response.status_code == 503 and attempt <= 3:
            # hold for some seconds and retry
            time.sleep(3**attempt)
            return put_into_api(line, attempt+1)

        else:
            return {'success': False, 'http_status': response.status_code, 'line': line, 'err': response.text}
    except requests.exceptions.ConnectionError as e:
        return {'success': False, 'err': 'Failed to connect to API'}

sent = jsonlines_rdd.map(put_into_api).cache()

count_success = sent.filter(lambda status_dict: status_dict['success']).count()
faileds = sent.filter(lambda status_dict: not status_dict['success'])
count_failure = faileds.count()

log.info('Sent {} lines with success!'.format(count_success))
log.info('Failed to post {} lines'.format(count_failure))

if count_failure > 1:
    log.info('Saving requests with failed status into "joboutput/{}/failed.json", please take a look'
            .format(job_datetime_str))
    faileds.map(json.dumps).saveAsTextFile('/joboutput/{}/failed.json'.format(job_datetime_str))
else:
    log.info('All posts executed with success!')
