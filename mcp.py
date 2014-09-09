#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The Master Control Program"""
import zmq
from zmq.eventloop import ioloop as ioloop_mod
import zmqdecorators
import zmq.utils.jsonapi as json

SERVICE_NAME='fi.iki.rambo.stresser.mcp'
METHODS_PORT=7070
SIGNALS_PORT=7071

class mcp(zmqdecorators.service):
    workers = []

    def __init__(self):
        super(mcp, self).__init__(SERVICE_NAME, service_port=METHODS_PORT)

        self.pcb = ioloop_mod.PeriodicCallback(self.testsignal, 1000)
        self.pcb.start()

    @zmqdecorators.signal(SERVICE_NAME, SIGNALS_PORT)
    def testsignal(self):
        print("Sending testsignal")
        pass

    @zmqdecorators.method()
    def emit_testsignal(self, resp, *args):
        resp.send("ok") # Not required
        self.testsignal()

    @zmqdecorators.method()
    def register_worker(self, resp, identity, *args):
        if not identity in self.workers:
            self.workers.append(identity)
            print("Worker %s registered, now have %d workers" % (identity, len(self.workers)))

    @zmqdecorators.method()
    def list_workers(self, resp, *args):
        resp.send(json.dumps(self.workers))

    def run(self):
        # Anything that needs to be handled *just* before we start the IOLopp, add it here
        super(mcp, self).run()


if __name__ == "__main__":
    # We will need a slightly lower level access
    instance = mcp()
    instance.run()
