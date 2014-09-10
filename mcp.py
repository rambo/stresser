#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The Master Control Program"""
import zmq
from zmq.eventloop import ioloop as ioloop_mod
import zmqdecorators
import zmq.utils.jsonapi as json
import time

DEAD_WORKER_TIMEOUT = 15 # Seconds

METHODS_SERVICE_NAME = 'fi.iki.rambo.stresser.mcp'
SIGNALS_SERVICE_NAME = 'fi.iki.rambo.stresser.mcp.signals'
METHODS_PORT = 7070
SIGNALS_PORT = 7071

class mcp(zmqdecorators.service):
    workers = {} # Keyed by identity, value is last heartbeat time

    def __init__(self):
        super(mcp, self).__init__(METHODS_SERVICE_NAME, service_port=METHODS_PORT)

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

    @zmqdecorators.signal(SIGNALS_SERVICE_NAME, SIGNALS_PORT)
    def worker_reaped(self, identity):
        """The gamemaster process is going to be interested in these signals"""
        pass

    @zmqdecorators.signal(SIGNALS_SERVICE_NAME, SIGNALS_PORT)
    def worker_added(self, identity):
        """The gamemaster process is going to be interested in these signals"""
        pass

    @zmqdecorators.signal(SIGNALS_SERVICE_NAME, SIGNALS_PORT)
    def testsignal(self, *args):
        print("Sending testsignal")
        pass

    @zmqdecorators.method()
    def emit_testsignal(self, resp, *args):
        resp.send("ok") # Not required
        self.testsignal("by request")

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
            print("Worker %s is alive" % identity)

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
