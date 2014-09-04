#!/usr/bin/env python
"""The Master Control Program"""
import zmq
from zmq.eventloop import ioloop
import zmqdecorators

SERVICE_NAME='rambo.stresser.mcp'

class mcp(object):
    def __init__(self, pub_wrapper):
        self.zmq_pub_wraper = pub_wrapper
        pass

    @zmqdecorators.signal(SERVICE_NAME)
    def testsignal(self):
        pass

    @zmqdecorators.method(SERVICE_NAME)
    def emit_testsignal(self, resp, *args):
        resp.send("ok") # Not required
        self.testsignal()

    def run(self):
        ioloop.IOLoop.instance().start()



if __name__ == "__main__":
    # We will need a slightly lower level access
    pub_wrapper = zmqdecorators.server_tracker.get_by_name_or_create(SERVICE_NAME, zmq.PUB)
    instance = mcp(pub_wrapper)
    instance.run()
