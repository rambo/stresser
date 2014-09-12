#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement
import zmq
import zmq.utils.jsonapi as json
from zmq.eventloop import ioloop as ioloop_mod

import zmqdecorators
import threading

from config import *


class gamemaster(zmqdecorators.client):
    def __init__(self, mcp_zmq_wrapper):
        super(gamemaster, self).__init__()
        self.mcp_zmq_wrapper = mcp_zmq_wrapper

    def get_worker(self, identity):
        return workerproxy(identity, self.mcp_zmq_wrapper)

    def call(self, *args):
        return zmqdecorators.call_sync(self.mcp_zmq_wrapper,  *args)

    def list_workers(self):
        return json.loads(self.call('list_workers')[0]).keys()



class workerproxy(object):
    identity = None
    mcp_zmq_wrapper = None

    def __init__(self, identity, mcp_zmq_wrapper):
        self.identity = identity
        self.mcp_zmq_wrapper = mcp_zmq_wrapper

    def cmd(self, cmd, *args):
        """The command arguments must be JSON encoded to be transferred via ZMQ"""
        #print("Calling self.mcp_zmq_wrapper.call('send_command', %s, %s, %s)" % (self.identity, cmd, json.dumps(*args)))
        zmqdecorators.call_sync(self.mcp_zmq_wrapper, 'send_command', self.identity, cmd, json.dumps(args))

if __name__ == "__main__":
    import sys,os

    # Handle the (optional) command line arguments
    if len(sys.argv) >= 2:
        # Manual IP & port config
        MCP_METHODS_SERVICE = (sys.argv[1], MCP_METHODS_PORT)
        MCP_SIGNALS_SERVICE = (sys.argv[1], MCP_SIGNALS_PORT)

    print("Connecting to MCP")
    mcp_zmq_wrapper = zmqdecorators.zmq_bonjour_connect_wrapper(zmq.DEALER, MCP_METHODS_SERVICE)
    print("Got MCP identity %s" % mcp_zmq_wrapper.socket.getsockopt(zmq.IDENTITY))
    gm = gamemaster(mcp_zmq_wrapper)
    e = gm.get_worker('EVERYONE')
    print("""e = gm.get_worker('EVERYONE') # proxy for all workers created """)
    print("""create new worker proxies: p = gm.get_worker('worker_id') """)
    print("""try: e.cmd('wd:get', 'http://www.aalto.fi/') # Note this, returns as soon as MCP has queued the message to workers""")

