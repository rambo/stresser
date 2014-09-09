#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Worker"""
import zmq
from zmq.eventloop import ioloop as ioloop_mod
import zmqdecorators
import zmq.utils.jsonapi as json
import datetime
import signal as posixsignal

# Hardcode IP
MCP_METHODS_SERVICE=('127.0.0.1', 7070)
# Bonjour resolving
MCP_METHODS_SERVICE='fi.iki.rambo.stresser.mcp'
# Hardcode IP
MCP_SIGNALS_SERVICE=('127.0.0.1', 7071)
# Bonjour resolving
MCP_SIGNALS_SERVICE='fi.iki.rambo.stresser.mcp'
# Hardcode IP
LOG_METHODS_SERVICE=('127.0.0.1', 7080)
# Bonjour resolving
LOG_METHODS_SERVICE='fi.iki.rambo.stresser.logger'

class worker(zmqdecorators.client):
    def __init__(self, mcp_wrapper, log_wrapper):
        super(worker, self).__init__()
        self.mcp_wrapper = mcp_wrapper
        self.log_wrapper = log_wrapper
        self.uuid = self.mcp_wrapper.uuid
        self.identity = self.mcp_wrapper.identity

        self.register_to_mcp()

        zmqdecorators.subscribe_topic(MCP_SIGNALS_SERVICE, 'testsignal', self.testsignal_callback)
        self.mcp_wrapper.call('emit_testsignal')

        zmqdecorators.subscribe_topic(MCP_SIGNALS_SERVICE, 'EVERYONE', self.mcp_command_callback)
        zmqdecorators.subscribe_topic(MCP_SIGNALS_SERVICE, self.identity, self.mcp_command_callback)
        self.log('N/A', 'STARTED', 0,0,0,0,0,'{}')

    def testsignal_callback(self, *args):
        print "Got testsignal: %s" % repr(args)

    def mcp_command_callback(self, *args):
        print "Got command: %s" % repr(args)

    def register_to_mcp(self):
        self.mcp_wrapper.call('register_worker', self.identity)

    def log(self, url, action, httpstatus, ttfb, ttlb, ttrdy, walltime, perfjson, timestamp=None):
        if not timestamp:
            timestamp = datetime.datetime.now()
        self.log_wrapper.call('log', timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:23], url, action, str(httpstatus), str(ttfb), str(ttlb), str(ttrdy), str(walltime), perfjson)

    def run(self):
        # Anything that needs to be handled *just* before we start the IOLopp, add it here
        super(worker, self).run()



if __name__ == "__main__":
    import sys,os
    # If started with an argument it is the IP for MCP & Logger
    if len(sys.argv) == 2:
        MCP_METHODS_SERVICE = (sys.argv[1], 7070)
        MCP_SIGNALS_SERVICE = (sys.argv[1], 7071)
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

