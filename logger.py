#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
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

SERVICE_NAME='fi.iki.rambo.stresser.mcp'
METHODS_PORT=7080
SIGNALS_PORT=7081


class logger(zmqdecorators.service):
    """Logs our status' etc to a sqlite database"""
    def __init__(self, logfilename):
        super(mcp, self).__init__(SERVICE_NAME, service_port=METHODS_PORT)

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
        #self.cursor.execute("CREATE TABLE status (sessionid INTEGER NOT NULL, time TIMESTAMP DATETIME DEFAULT(STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')), responsetime INTEGER, ioerror INTEGER, httpstatus INTEGER, contentstatus BOOLEAN, FOREIGN KEY(sessionid) REFERENCES sessions(id));")
        self.connection.commit()

    @zmqdecorators.method()
    def log(self, resp, *args):
        pass

    def run(self):
        ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    instance = logger()
    instance.run()

