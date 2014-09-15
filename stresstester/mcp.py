#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The Master Control Program"""
from __future__ import with_statement
import zmq
from zmq.eventloop import ioloop as ioloop_mod
import zmqdecorators
import zmq.utils.jsonapi as json
import time


DEAD_WORKER_TIMEOUT = 15 # Seconds

from config import *
METHODS_SERVICE_NAME = MCP_METHODS_SERVICE
SIGNALS_SERVICE_NAME = MCP_SIGNALS_SERVICE
METHODS_PORT = MCP_METHODS_PORT
SIGNALS_PORT = MCP_SIGNALS_PORT

class mcp(zmqdecorators.service):
    workers = {} # Keyed by identity, value is last heartbeat time
    signals_stream = None 

    def __init__(self):
        super(mcp, self).__init__(METHODS_SERVICE_NAME, service_port=METHODS_PORT)

        # This is low-level ZMQStream, to be used only in special cases
        self.signals_stream = zmqdecorators.server_tracker.get_by_name(SIGNALS_SERVICE_NAME, zmq.PUB).stream

        # periodically reap dead workers from our registry
        self.reaper_pcb = ioloop_mod.PeriodicCallback(self.reap_dead_workers, 1000)
        self.reaper_pcb.start()

    def reap_dead_workers(self):
        now = time.time()
        reaped = False
        for identity in self.workers.keys(): # We must get they keys as list because changing the dict while we're iterating over it is forbidden
            if ((now - self.workers[identity]) > DEAD_WORKER_TIMEOUT):
                print("Worker %s is DEAD, reaping" % identity)
                del(self.workers[identity])
                self.worker_reaped(identity)
                reaped = True
        if reaped:
            print("Now have %d workers" % len(self.workers))

    def _send_command(self, identity, command, *args):
        """Send command to given worker (or 'EVERYONE'), uses PUB socket. This is the actual implementation (separate from the RPC method so we can call it directly as needed)"""
        #print("Sending command %s to %s (args: %s)" % (command, identity, repr(args)))
        self.signals_stream.send_multipart([identity, command] + list(args))

    @zmqdecorators.method()
    def send_command(self, resp, identity, command, *args):
        """Send command to given worker (or 'EVERYONE'), uses PUB socket. This is what gamemester calls to delegate commands, the final argument must be JSON encoded argument list for the command method"""
        #print("send_command called by %s" % resp.client_id)
        self._send_command(identity, command, *args)
        resp.send("sent")

    @zmqdecorators.signal(SIGNALS_SERVICE_NAME, SIGNALS_PORT)
    def worker_reaped(self, identity):
        """The gamemaster process is going to be interested in these signals"""
        pass

    @zmqdecorators.signal(SIGNALS_SERVICE_NAME, SIGNALS_PORT)
    def worker_added(self, identity):
        """The gamemaster process is going to be interested in these signals"""
        pass

    @zmqdecorators.method()
    def register_worker(self, resp, identity, *args):
        if not self.workers.has_key(identity):
            self.workers[identity] = time.time()
            print("Worker %s registered, now have %d workers" % (identity, len(self.workers)))
            self.worker_added(identity)
        else:
            print("Worker %s already registered")

    @zmqdecorators.method()
    def worker_heatbeat(self, resp, identity, *args):
        if not self.workers.has_key(identity):
            self.workers[identity] = time.time()
            print("Worker %s sent heartbeat but was not registered, now have %d workers" % (identity, len(self.workers)))
            self.worker_added(identity)
        else:
            self.workers[identity] = time.time()
            #print("Worker %s is alive" % identity)

    @zmqdecorators.method()
    def list_workers(self, resp, *args):
        resp.send(json.dumps(self.workers))

    def run(self):
        # Anything that needs to be handled *just* before we start the IOLopp, add it here
        super(mcp, self).run()


if __name__ == "__main__":
    # We will need a slightly lower level access
    instance = mcp()
    print("Starting IOLoop")
    instance.run()
