# Client

**Putter JOB** `putter/putter_job.py`

Spark job that process jsonlines file and post data to API

Job requires 3 args:
- API host and port to post data
- resource API path (host:port/**model1s**)
- jsonline file

Environment requirements:
- HBase docker running
- API docker running

**Run job with sample in docker**

    make setup-venv
    source venv/bin/activate
    ./generate_jsonlines.py
    ./client.py localhost:8000 model1s sample.jsonl

- make setup-venv: will setup virtual env with requirements.
- generate_jsonlines.py: create a file containing json model1 schema lines
- client.py: execute job in a spark docker container


### TODO:
 - [x] generate jsonlines files
 - [x] send each line/data/model to API
 - [x] save failed posts into files with reasons
 - [ ] send batch/bulk of lines/data/model to API
