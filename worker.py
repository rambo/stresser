#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Worker"""
import zmq
from zmq.eventloop import ioloop
import zmqdecorators
import zmq.utils.jsonapi as json
import datetime

# Hardcode IP
MCP_METHODS_SERVICE=('127.0.0.1', 7070)
# Bonjour resolving
MCP_METHODS_SERVICE='fi.iki.rambo.stresser.mcp'

# Hardcode IP
LOG_METHODS_SERVICE=('127.0.0.1', 7080)
# Bonjour resolving
LOG_METHODS_SERVICE='fi.iki.rambo.stresser.logger'

class worker(object):
    def __init__(self, mcp_wrapper, log_wrapper):
        self.mcp_wrapper = mcp_wrapper
        self.log_wrapper = log_wrapper
        self.uuid = self.mcp_wrapper.uuid
        self.identity = self.mcp_wrapper.identity

        self.register_to_mcp()
        self.log('NA', 'STARTED', 200, 0,0,0, '{}')

    def register_to_mcp(self):
        self.mcp_wrapper.call('register_worker', self.identity)

    def log(self, url, action, httpstatus, ttfb, ttlb, ttrdy, perfjson, timestamp=None):
        if not timestamp:
            timestamp = datetime.datetime.now()
        self.log_wrapper.call('log', timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:23], url, action, str(httpstatus), str(ttfb), str(ttlb), str(ttrdy), perfjson)

    def run(self):
        ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    import sys,os
    # If started with an argument it is the IP for MCP & Logger
    if len(sys.argv) == 2:
        MCP_METHODS_SERVICE = (sys.argv[1], 7070)
        LOG_METHODS_SERVICE = (sys.argv[1], 7080)
    # We will need a slightly lower level access
    print("Connecting to MCP")
    mcp_wrapper = zmqdecorators.zmq_bonjour_connect_wrapper(zmq.DEALER, MCP_METHODS_SERVICE)
    print("Got MCP identity %s" % mcp_wrapper.socket.getsockopt(zmq.IDENTITY))
    print("Connecting to logger")
    log_wrapper = zmqdecorators.zmq_bonjour_connect_wrapper(zmq.DEALER, LOG_METHODS_SERVICE, identity=mcp_wrapper.identity)
    print("Got LOG identity %s" % log_wrapper.socket.getsockopt(zmq.IDENTITY))
    instance = worker(mcp_wrapper, log_wrapper)
    instance.run()

