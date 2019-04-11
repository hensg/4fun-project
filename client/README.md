# Client

**Putter JOB** `putter/putter_job.py`

Process jsonlines and post data to API

Job requires 3 args:
- API host and port to post data
- data model resource API path (host:port/**model1**)
- jsonline file

**Run job with sample in docker**

  make setup-venv
  source venv/bin/activate
  ./generate_jsonlines.py
  ./client.py localhost:8000 model1 sample.jsonl

- make setup-venv: will setup virtual env with requirements.
- generate_jsonlines.py: create a file containing json model1 lines
- client.py: execute job in spark docker container

* Requires HBase and API docker running

### TODO:
 - [x] generate jsonlines files
 - [x] send each line/data/model to API
 - [x] save failed posts into files with reasons
 - [ ] send batch/bulk of lines/data/model to API
