#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement
import zmq.utils.jsonapi as json

# Bonjour resolving
MCP_METHODS_SERVICE = 'fi.iki.rambo.stresser.mcp'
MCP_SIGNALS_SERVICE = 'fi.iki.rambo.stresser.mcp.signals'
LOG_METHODS_SERVICE = 'fi.iki.rambo.stresser.logger'


class workerproxy(object)
    identity = None
    mcp_wrapper = None
    
    def __init__(self, identity, mcp_wrapper):
        self.identity = identity
        self.mcp_wrapper = mcp_wrapper

    def cmd(self, cmd, *args):
        """The command arguments must be JSON encoded to be transferred via ZMQ"""
        self.mcp_wrapper.call('send_command', self.identity, cmd, json.dumps(*args))
        


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
    
    mcp = mcp_wrapper
    e = workerproxy('EVERYONE', mcp_wrapper)
    print("""create new proxies: e = workerproxy('EVERYONE', mcp_wrapper) """)
    print("""try: e.cmd('wd:get', 'http://www.aalto.fi/')
