#!venv/bin/python3.6

import os
import argparse
import docker

parser = argparse.ArgumentParser(
       description='Process some files and send data to API'
)
parser.add_argument('api_host', type=str,
       help='API host:port endpoint to send data')
parser.add_argument('path', type=str,
       help='Paths with jsonlines files to process')
parser.add_argument('--overwrite-if-exists', default=False, action="store_true",
       help='Overwrite data if exists') 

args = parser.parse_args()

host = args.api_host
path = args.path
overwrite_if_exists = args.overwrite_if_exists

DOCKER_IMAGE_NAME='client-putter'

pwd = os.path.dirname(os.path.abspath(__file__))

dc = docker.from_env()
try:
    dc.images.get(DOCKER_IMAGE_NAME)
except docker.errors.ImageNotFound:
    print('Putter job image not found...building it (client-putter)')
    _, logs = dc.images.build(path='{}/putter/'.format(pwd), tag=DOCKER_IMAGE_NAME)
    print(logs)

c = dc.containers.run(
    image=DOCKER_IMAGE_NAME,
    command='/putter_job.py {} /{}'.format(host, path),
    network_mode='host',
    remove=True,
    detach=True,
    volumes=[
        '{}/joboutput:/joboutput'.format(pwd),
        '{}/putter/putter_job.py:/putter_job.py'.format(pwd),
        '{}:/{}'.format(pwd + '/' + path, path)
    ])
for l in c.logs(stream=True):
    print(l)
