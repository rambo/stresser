"""Worker"""
import zmq
from zmq.eventloop import ioloop
import zmqdecorators

SERVICE_NAME='rambo.stresser.mcp'

class worker(object):
    def __init__(self, client_wrapper):
        self.zmq_wraper = client_wrapper
        pass

    def run(self):
        ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    # We will need a slightly lower level access
    client_wrapper = zmqdecorators.zmq_bonjour_connect_wrapper(zmq.DEALER, 'rambo.stresser.mcp')
    instance = worker(client_wrapper)
    instance.run()

