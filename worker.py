#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Worker"""
from __future__ import with_statement
import zmq
from zmq.eventloop import ioloop as ioloop_mod
import zmqdecorators
import zmq.utils.jsonapi as json
import datetime
import atexit
import signal as posixsignal
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import selenium.common.exceptions as seleniumexceptions
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from threading import Lock


REMOTE = 'http://127.0.0.1:4444/wd/hub'
CAPS = DesiredCapabilities.FIREFOX

# Bonjour resolving
MCP_METHODS_SERVICE = 'fi.iki.rambo.stresser.mcp'
MCP_SIGNALS_SERVICE = 'fi.iki.rambo.stresser.mcp.signals'
LOG_METHODS_SERVICE = 'fi.iki.rambo.stresser.logger'

class worker(zmqdecorators.client):
    webdriver = None
    previus_source = None

    def __init__(self, mcp_wrapper, log_wrapper):
        super(worker, self).__init__()
        self.mcp_wrapper = mcp_wrapper
        self.log_wrapper = log_wrapper
        self.uuid = self.mcp_wrapper.uuid
        self.identity = self.mcp_wrapper.identity
        self.webdriver_lock = Lock()

        print("Connecting to Webdriver %s" % REMOTE)
        self.webdriver = webdriver.Remote(desired_capabilities=CAPS, command_executor=REMOTE)
        atexit.register(self.webdriver.quit)

        # Subscribe to the command PUB channels
        zmqdecorators.subscribe_topic(MCP_SIGNALS_SERVICE, 'EVERYONE', self.mcp_command_callback)
        zmqdecorators.subscribe_topic(MCP_SIGNALS_SERVICE, self.identity, self.mcp_command_callback)
        # Register to the MCP via RPC call
        self.register_to_mcp()

        # Send heartbeats
        self.heartbeat_pcb = ioloop_mod.PeriodicCallback(self.heartbeat_to_mcp, 1000)
        self.heartbeat_pcb.start()

        # Finally log us as a started worker
        self.log('N/A', 'STARTED', 0,0,0,0,0,'{}')

    def page_changed(self):
        """Checks if the DOM(?) has changed since last check"""
        new_source = self.webdriver.page_source
        ret = True
        if self.previus_source == new_source:
            ret = False
        self.previus_source = new_source
        return ret

    def mcp_command_callback(self, identity, command, args_json="[]"):
        args = jsonapi.loads(args_json)
        print "Got command: %s(%s)" % (command, repr(args))
        start = time.time()
        with self.webdriver_lock:
            if command[0:3] == 'wd:':
                logaction = command
                cmdmethod = self.webdriver.getattr(command[3:])
            else:
                logaction = "%s:%s" % (self.wd_last_return.id, command)
                cmdmethod = self.wd_last_return.getattr(command)
            self.wd_last_return = cmdmethod(*args)
            walltime = time.time() - start
            # Log results if page was change or command was in certain list
            if (   self.page_changed()
                or command in ('wd:get', 'click')):
                # For HTTP status codes we need a proxy that will give that info to us (like browsermob-proxy or something)
                self.log(self.webdriver.current_url, logaction, 0, walltime, *self.get_performance())

    def register_to_mcp(self):
        self.mcp_wrapper.call('register_worker', self.identity)

    def heartbeat_to_mcp(self):
        self.mcp_wrapper.call('worker_heatbeat', self.identity)

    def log(self, url, action, httpstatus, walltime, ttfb, ttlb, ttrdy, perfjson, timestamp=None):
        if not timestamp:
            timestamp = datetime.datetime.now()
        self.log_wrapper.call('log', timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:23], url, action, str(httpstatus), str(walltime), str(ttfb), str(ttlb), str(ttrdy), perfjson)

    # from http://stackoverflow.com/questions/11360854/right-way-to-test-page-load-time-in-selenium
    def get_performance(self):
        """Read the window.performance data from browser and calculate some values while at it, pre-encodes the performance full performance data to JSON so the return value can be passed to self.log"""
        perf = self.webdriver.execute_script("""var performance = window.performance || {}; var timings = performance.timing || {}; return timings;""")
        ttfb = perf[u'responseStart'] - perf[u'fetchStart']
        ttlb = perf[u'responseEnd'] - perf[u'fetchStart']
        ttrdy = perf[u'loadEventEnd'] - perf[u'fetchStart']
        return (ttfb, ttlb, ttrdy, json.dumps(perf))

    def cleanup(self):
# Atexit will take care of this
#        if self.webdriver:
#            self.webdriver.quit()
        pass

    def run(self):
        # Anything that needs to be handled *just* before we start the IOLopp, add it here
        super(worker, self).run()



if __name__ == "__main__":
    import sys,os

    # Handle the (optional) command line arguments
    if len(sys.argv) >= 2:
        # Manual IP & port config
        MCP_METHODS_SERVICE = (sys.argv[1], 7070)
        MCP_SIGNALS_SERVICE = (sys.argv[1], 7071)
        LOG_METHODS_SERVICE = (sys.argv[1], 7080)
    if len(sys.argv) >= 3:
        # Alternate IP for the Selenium hub
        REMOTE='http://%s:4444/wd/hub' % sys.argv[2]

    print("Connecting to MCP")
    mcp_wrapper = zmqdecorators.zmq_bonjour_connect_wrapper(zmq.DEALER, MCP_METHODS_SERVICE)
    print("Got MCP identity %s" % mcp_wrapper.socket.getsockopt(zmq.IDENTITY))
    print("Connecting to logger")
    log_wrapper = zmqdecorators.zmq_bonjour_connect_wrapper(zmq.DEALER, LOG_METHODS_SERVICE, identity=mcp_wrapper.identity)
    print("Got LOG identity %s" % log_wrapper.socket.getsockopt(zmq.IDENTITY))
    instance = worker(mcp_wrapper, log_wrapper)
    print("Starting eventloop")
    instance.run()

