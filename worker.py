"""Worker"""
import zmq
from zmq.eventloop import ioloop
import zmqdecorators
import zmq.utils.jsonapi as json


SERVICE_NAME='rambo.stresser.mcp'

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
    # We will need a slightly lower level access
    client_wrapper = zmqdecorators.zmq_bonjour_connect_wrapper(zmq.DEALER, 'fi.iki.rambo.stresser.mcp')
    print("Got identity %s" % client_wrapper.socket.getsockopt(zmq.IDENTITY))
    instance = worker(client_wrapper)
    instance.run()

