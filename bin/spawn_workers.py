#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing
import worker
from config import *
import signal as posixsignal
from exceptions import RuntimeError,KeyboardInterrupt

def run_worker():
    instance = worker.worker()
    p = multiprocessing.current_process()
    print("Starting eventloop in %s %d" % (p.name, p.pid))
    instance.run()



class workerpool(object):
    subprocesses = []

    def startn(self, n):
        """Spawns N worker subsprocesses"""
        for x in range(n):
            p = multiprocessing.Process(target=run_worker)
            self.subprocesses.append(p)
            p.start()

    def quit(self, *args):
        """Sends SIGTERM to all workers"""
        for w in self.subprocesses:
            w.terminate()

    def join_all(self):
        """Waits for .join() for all workers"""
        posixsignal.signal(posixsignal.SIGTERM, self.quit)
        posixsignal.signal(posixsignal.SIGQUIT, self.quit)
        for w in self.subprocesses:
            w.join()



if __name__ == "__main__":
    import sys,os
    if len(sys.argv) < 2:
        print("Call with the number of workers to spawn")
        sys.exit(1)

    # Handle the (optional) command line arguments
    if len(sys.argv) >= 3:
        # Manual IP & port config
        worker.MCP_METHODS_SERVICE = (sys.argv[2], MCP_METHODS_PORT)
        worker.MCP_SIGNALS_SERVICE = (sys.argv[2], MCP_SIGNALS_PORT)
        worker.LOG_METHODS_SERVICE = (sys.argv[2], LOG_METHODS_PORT)
    if len(sys.argv) >= 4:
        # Alternate IP for the Selenium hub
        worker.REMOTE='http://%s:4444/wd/hub' % sys.argv[3]

    pool = workerpool()
    pool.startn(int(sys.argv[1]))

    try:
        pool.join_all()
    except KeyboardInterrupt:
        pool.quit()
        pool.join_all()


