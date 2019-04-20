import logging
import json
import falcon
from happybase import NoConnectionsAvailable

class Status:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def on_get(self, req, resp):
        hstatus = False
        try:
            with self.db_manager.pool().connection() as conn:
                hstatus = True
        except Exception as e:
            logging.exception(e)

        resp.body = json.dumps({
            'hbase-on': hstatus,
            'api-on': True
        })
        resp.status = falcon.HTTP_200
