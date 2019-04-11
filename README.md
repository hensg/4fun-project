# Project

An API written in Python 3.6 using falcon framework,
The API receives JSON (`api/app/schemas/model1.json`),
validate it and save into HBase.

The main idea here is to store a huge amount of data
with scalability and good performance to read/write
based on a KEY (non-relational).

### Playing with docker - instructions:

*requirements: docker, docker-composer

1. Build API image

  docker-compose build


2. Run HBase, Prometheus and API

  docker-compose up


3. Create tables **Important**

At first time, it's required to create tables running the following script after hbase started:

  ./create_tables.sh  

4. Execute client - Read more: client/README.md

  
### api/

Contains API code

Read more: api/README.md

### client/

An job that process jsonline files and send it to API

Read more: client/README.md

### database/

Folder to store database data and create table instructions

### prometheus/

Contains prometheus configuration to scrap API metrics

-------
## TODO:
- [x] post collection
- [x] get collection (sample)
- [x] put item
- [x] get item
- [x] metrics
- [x] tests
- [x] linter
- [ ] batch/bulk post collection - **batch should be used to put into HBase**
- [ ] CI
