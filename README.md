# Project
[![CircleCI](https://circleci.com/gh/hensg/4fun-project.svg?style=shield&circle-token=eec193b24cd71729f92ccc6b1345df4ecc57c2d4)](https://circleci.com/gh/hensg/4fun-project)

An API written in Python 3.6 using falcon framework.

The API receives JSON body, validate(`api/app/schemas/model1.json`) it 
and save into HBase.

The main idea here is to store a huge amount of data
with scalability and good performance to read/write
based on a KEY (non-relational).

### Playing with docker - instructions:

Requirements:
- docker
- docker-composer

Steps:

1. Build API image


        docker-compose build


2. Run HBase, Prometheus and API


        docker-compose up


3. Create tables **Important**

It's required to create tables running the following script after hbase started:

       ./create_tables.sh


4. Execute client - Read more: client/README.md

### TODO:
- [x] post collection
- [x] get collection (sample)
- [x] put item
- [x] get item
- [x] metrics
- [x] tests
- [x] linter
- [ ] remove hardcoded configs
- [ ] batch/bulk post collection - *batch should be used to put into HBase*
- [ ] authentication with token/ldap/oauth/...
- [ ] authorization
- [ ] CI
  
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
