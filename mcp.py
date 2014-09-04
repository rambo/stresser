#!/usr/bin/env python
"""The Master Control Program"""
import zmq
from zmq.eventloop import ioloop
import zmqdecorators
import zmq.utils.jsonapi as json

SERVICE_NAME='fi.iki.rambo.stresser.mcp'

class mcp(zmqdecorators.service):
    workers = []

    def __init__(self):
        super(mcp, self).__init__(SERVICE_NAME)
        pass

    @zmqdecorators.signal(SERVICE_NAME)
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
        ioloop.IOLoop.instance().start()



if __name__ == "__main__":
    # We will need a slightly lower level access
    instance = mcp()
    instance.run()