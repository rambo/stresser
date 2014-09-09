#!/usr/bin/env python
# -*- coding: utf-8 -*-
from exceptions import NotImplementedError,RuntimeError
import sqlite3
# Decimal recipe from http://stackoverflow.com/questions/6319409/how-to-convert-python-decimal-to-sqlite-numeric
#import decimal
# Register the adapter
#sqlite3.register_adapter(decimal.Decimal, lambda d: str(d))
# Register the converter
#sqlite3.register_converter("NUMERIC", lambda s: decimal.Decimal(s))
# Register converter&adapter for datetime in the same way
import datetime
sqlite3.register_adapter(datetime.datetime, lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:23])
# The type on SQLite is "TIMESTAMP" even if we specified "DATETIME" in table creation...
sqlite3.register_converter("TIMESTAMP", lambda s: datetime.datetime.strptime(s.ljust(26,"0"), "%Y-%m-%d %H:%M:%S.%f"))

import zmq
from zmq.eventloop import ioloop
import zmqdecorators
import zmq.utils.jsonapi as json

SERVICE_NAME='fi.iki.rambo.stresser.logger'
METHODS_PORT=7080
SIGNALS_PORT=7081


class logger(zmqdecorators.service):
    """Logs our status' etc to a sqlite database"""
    def __init__(self, logfilename):
        super(logger, self).__init__(SERVICE_NAME, service_port=METHODS_PORT)

        call_init_db = False
        if not os.path.exists(logfilename):
            call_init_db = True
        self.connection = sqlite3.connect(logfilename, detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self.connection.cursor()
        if call_init_db:
            self.init_db()

    def init_db(self):
        """Initializes the database schema"""
        # The timestamps on these tables are basically denormalized just in case we wish to do optimized time based searches in them.
        # TODO: Rethink the schema
        self.cursor.execute("CREATE TABLE log (clientid TEXT NOT NULL, time TIMESTAMP DATETIME DEFAULT(STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')), url TEXT, action TEXT, httpstatus INTEGER, ttfb INTEGER, ttlb INTEGER, ttrdy INTEGER, walltime INTEGER, perfjson TEXT);")
        self.connection.commit()

    @zmqdecorators.method()
    def log(self, resp, timestamp, url, action, httpstatus, ttfb, ttlb, ttrdy, walltime, perfjson):
        self.cursor.execute("INSERT INTO log (clientid, time, url, action, httpstatus, ttfb, ttlb, ttrdy, walltime, perfjson) VALUES (?,?,?,?,?,?,?,?,?,?);", (resp.client_id, timestamp, url, action, int(httpstatus), int(ttfb), int(ttlb), int(ttrdy), int(walltime), perfjson))
        self.connection.commit()



if __name__ == "__main__":
    import sys, os, os.path
    if len(sys.argv) < 2:
        logfile = "%s-%s.db" % (os.path.splitext(os.path.basename(sys.argv[0]))[0], datetime.datetime.now().strftime("%Y%m%d_%H%M"))
    else:
        logfile = sys.argv[1]
    instance = logger(logfile)
    instance.run()

