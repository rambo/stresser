#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement
import zmq
import zmq.utils.jsonapi as json
from zmq.eventloop import ioloop as ioloop_mod

import zmqdecorators
import threading

# Bonjour resolving
MCP_METHODS_SERVICE = 'fi.iki.rambo.stresser.mcp'
MCP_SIGNALS_SERVICE = 'fi.iki.rambo.stresser.mcp.signals'
LOG_METHODS_SERVICE = 'fi.iki.rambo.stresser.logger'


class gamemaster(zmqdecorators.client):
    def __init__(self, mcp_wrapper):
        super(gamemaster, self).__init__()
        self.mcp_wrapper = mcp_wrapper

    def get_proxy(self, identity):
        return workerproxy(identity, self.mcp_wrapper)

class workerproxy(object):
    identity = None
    mcp_wrapper = None
    
    def __init__(self, identity, mcp_wrapper):
        self.identity = identity
        self.mcp_wrapper = mcp_wrapper

    def cmd(self, cmd, *args):
        """The command arguments must be JSON encoded to be transferred via ZMQ"""
        #print("Calling self.mcp_wrapper.call('send_command', %s, %s, %s)" % (self.identity, cmd, json.dumps(*args)))
        zmqdecorators.call_sync(self.mcp_wrapper, 'send_command', self.identity, cmd, json.dumps(args))



if __name__ == "__main__":
    import sys,os

    # Handle the (optional) command line arguments
    if len(sys.argv) >= 2:
        # Manual IP & port config
        MCP_METHODS_SERVICE = (sys.argv[1], 7070)
        MCP_SIGNALS_SERVICE = (sys.argv[1], 7071)
        LOG_METHODS_SERVICE = (sys.argv[1], 7080)

    print("Connecting to MCP")
    mcp_wrapper = zmqdecorators.zmq_bonjour_connect_wrapper(zmq.DEALER, MCP_METHODS_SERVICE)
    print("Got MCP identity %s" % mcp_wrapper.socket.getsockopt(zmq.IDENTITY))
    gm = gamemaster(mcp_wrapper)
    e = gm.get_proxy('EVERYONE')
    print("""e = gm.get_proxy('EVERYONE') # proxy for all workers created """)
    print("""create new proxies: p = gm.get_proxy('worker_id') """)
    print("""try: e.cmd('wd:get', 'http://www.aalto.fi/') # Note this, returns as soon as MCP has queued the message to workers""")

