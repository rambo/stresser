#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Worker"""
from __future__ import with_statement
import zmq
import zmq.utils.jsonapi as json
from zmq.eventloop import ioloop as ioloop_mod
import zmqdecorators
import time, datetime
import atexit
import signal as posixsignal
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import selenium.common.exceptions as seleniumexceptions
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from threading import Lock
from exceptions import RuntimeError,KeyboardInterrupt,AttributeError

REMOTE = 'http://127.0.0.1:4444/wd/hub'
CAPS = DesiredCapabilities.FIREFOX

from config import *


class worker(zmqdecorators.client):
    webdriver = None
    previus_source = None

    def __init__(self):
        super(worker, self).__init__()

        print("Connecting to MCP")
        self.mcp_wrapper = zmqdecorators.zmq_bonjour_connect_wrapper(zmq.DEALER, MCP_METHODS_SERVICE)
        print("Got MCP identity %s" % self.mcp_wrapper.socket.getsockopt(zmq.IDENTITY))
        print("Connecting to logger")
        self.log_wrapper = zmqdecorators.zmq_bonjour_connect_wrapper(zmq.DEALER, LOG_METHODS_SERVICE, identity=self.mcp_wrapper.identity)
        print("Got LOG identity %s" % self.log_wrapper.socket.getsockopt(zmq.IDENTITY))

        self.uuid = self.mcp_wrapper.uuid
        self.identity = self.mcp_wrapper.identity
        self.webdriver_lock = Lock()

        print("Connecting to Webdriver %s" % REMOTE)
        self.webdriver = webdriver.Remote(desired_capabilities=CAPS, command_executor=REMOTE)
        # This does not work for subprocesses it seems
        # atexit.register(self.webdriver.quit)

        # Subscribe to the command PUB channels
        zmqdecorators.subscribe_topic(MCP_SIGNALS_SERVICE, 'EVERYONE', self.mcp_command_callback)
        zmqdecorators.subscribe_topic(MCP_SIGNALS_SERVICE, self.identity, self.mcp_command_callback)
        # Register to the MCP via RPC call
        self.register_to_mcp()

        # Send heartbeats
        self.heartbeat_pcb = ioloop_mod.PeriodicCallback(self.heartbeat_to_mcp, 1000)
        self.heartbeat_pcb.start()

        # Keep the webdriver connection alive
        self.wdkeepalive_pcb = ioloop_mod.PeriodicCallback(self._webdriver_keepalive, 5000)
        self.wdkeepalive_pcb.start()

        # Finally log us as a started worker
        self.log('N/A', 'STARTED', '{}', 0,0,0,0,0,'{}')


    def _webdriver_keepalive(self):
        """Just call driver.title to keep the webdriver connection alive"""
        with self.webdriver_lock:
            self.webdriver.title


    def page_changed(self):
        """Checks if the DOM(?) has changed since last check"""
        new_source = self.webdriver.page_source
        ret = True
        if self.previus_source == new_source:
            ret = False
        self.previus_source = new_source
        return ret

    def DIE(self):
        """Kill a worker remotely"""
        print("quitting...")
        self.quit()

    def mcp_command_callback(self, command, args_json="[]"):
        args = json.loads(args_json)
        print("Got command: %s(*%s)" % (command, repr(args)))
        try:
            # Check if we have a special handler for this command
            mymethod = getattr(self, command)
            return mymethod(*args)
        except AttributeError:
            pass
        # Otherwise try to be smart
        start = time.time()
        with self.webdriver_lock:
            if command[0:3] == 'wd:':
                logaction = command
                cmdmethod = getattr(self.webdriver, command[3:])
            else:
                logaction = "%s:%s" % (self.wd_last_return.id, command)
                cmdmethod = getattr(self.wd_last_return, command)
            self.wd_last_return = cmdmethod(*args)
            walltime = time.time() - start
            walltime_ms = int(walltime*1000)
            # Log results if page was change or command was in certain list
            if (   self.page_changed()
                or command in ('wd:get', 'click')):
                # For HTTP status codes we need a proxy that will give that info to us (like browsermob-proxy or something)
                # use milliseconds as walltime unit too
                self.log(self.webdriver.current_url, logaction, args_json, 0, walltime_ms, *self.get_performance()) 

    def register_to_mcp(self):
        self.mcp_wrapper.call('register_worker', self.identity)

    def heartbeat_to_mcp(self):
        self.mcp_wrapper.call('worker_heatbeat', self.identity)

    def log(self, url, action, args_json, httpstatus, walltime, ttfb, ttlb, ttrdy, perfjson, timestamp=None):
        if not timestamp:
            timestamp = datetime.datetime.now()
        self.log_wrapper.call('log', timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:23], str(url), str(action), str(args_json), str(httpstatus), str(walltime), str(ttfb), str(ttlb), str(ttrdy), str(perfjson))

    # from http://stackoverflow.com/questions/11360854/right-way-to-test-page-load-time-in-selenium
    def get_performance(self):
        """Read the window.performance data from browser and calculate some values while at it, pre-encodes the performance full performance data to JSON so the return value can be passed to self.log"""
        perf = self.webdriver.execute_script("""var performance = window.performance || {}; var timings = performance.timing || {}; return timings;""")
        ttfb = perf[u'responseStart'] - perf[u'fetchStart']
        ttlb = perf[u'responseEnd'] - perf[u'fetchStart']
        ttrdy = perf[u'loadEventEnd'] - perf[u'fetchStart']
        return (ttfb, ttlb, ttrdy, json.dumps(perf))

    def cleanup(self):
        if self.webdriver:
            self.webdriver.quit()
        pass

    def run(self):
        # Anything that needs to be handled *just* before we start the IOLopp, add it here
        super(worker, self).run()



if __name__ == "__main__":
    import sys,os

    # Handle the (optional) command line arguments
    if len(sys.argv) >= 2:
        # Manual IP & port config
        MCP_METHODS_SERVICE = (sys.argv[1], MCP_METHODS_PORT)
        MCP_SIGNALS_SERVICE = (sys.argv[1], MCP_SIGNALS_PORT)
        LOG_METHODS_SERVICE = (sys.argv[1], LOG_METHODS_PORT)
    if len(sys.argv) >= 3:
        # Alternate IP for the Selenium hub
        REMOTE='http://%s:4444/wd/hub' % sys.argv[2]

    instance = worker()
    print("Starting eventloop")
    instance.run()

