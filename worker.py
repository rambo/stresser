#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Worker"""
import zmq
from zmq.eventloop import ioloop
import zmqdecorators
import zmq.utils.jsonapi as json

# Hardcode IP
METHODS_SERVICE=('127.0.0.1', 7070)
# Bonjour resolving
METHODS_SERVICE='fi.iki.rambo.stresser.mcp'

class worker(object):
    def __init__(self, client_wrapper):
        self.zmq_wrapper = client_wrapper
        self.uuid = self.zmq_wrapper.uuid
        self.identity = self.zmq_wrapper.identity
        
        self.register_to_mcp()

    def register_to_mcp(self):
        self.zmq_wrapper.call('register_worker', self.identity)

    def run(self):
        ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    import sys,os
    # If started with an argument it is the IP for MCP
    if len(sys.argv) == 2:
        METHODS_SERVICE = (sys.argv[1], 7070)
    # We will need a slightly lower level access
    client_wrapper = zmqdecorators.zmq_bonjour_connect_wrapper(zmq.DEALER, METHODS_SERVICE)
    print("Got identity %s" % client_wrapper.socket.getsockopt(zmq.IDENTITY))
    instance = worker(client_wrapper)
    instance.run()

