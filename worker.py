"""Worker"""
import zmq
from zmq.eventloop import ioloop
import zmqdecorators
import zmq.utils.jsonapi as json

# Bonjour resolving
METHODS_SERVICE='fi.iki.rambo.stresser.mcp'
# Hardcode IP
METHODS_SERVICE=('127.0.0.1', 7070)

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
    # We will need a slightly lower level access
    client_wrapper = zmqdecorators.zmq_bonjour_connect_wrapper(zmq.DEALER, METHODS_SERVICE)
    print("Got identity %s" % client_wrapper.socket.getsockopt(zmq.IDENTITY))
    instance = worker(client_wrapper)
    instance.run()

