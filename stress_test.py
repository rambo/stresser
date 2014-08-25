#!/usr/bin/env python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time, datetime
import multiprocessing
import sys,os

REMOTE='http://10.211.55.14:4444/wd/hub'


def getn(url, n):
    import atexit
    p = multiprocessing.current_process()
    print 'Starting:', p.name, p.pid
    sys.stdout.flush()
    driver = webdriver.Remote(
                    desired_capabilities=DesiredCapabilities.FIREFOX,
                    command_executor=REMOTE
    )
    # This doesn't seem to work with multiprocessing...
    atexit.register(driver.quit)
    print 'Ready:', p.name, p.pid
    sys.stdout.flush()
    for i in range(n):
        b = time.time()
        driver.get(url)
        took = time.time() - b
        print "pid %d, time %f: got %s in %f seconds" % (p.pid, time.time(), url, took)
        b = time.time()
        fname = "%d_%s.png" % (p.pid,datetime.datetime.now().isoformat())
        took = time.time() - b
        driver.get_screenshot_as_file(fname)
        print "pid %d, time %f: dumped %s in %f seconds" % (p.pid, time.time(), fname, took)

    time.sleep(20)
    fname = "%d_%s.png" % (p.pid,datetime.datetime.now().isoformat())
    driver.get_screenshot_as_file(fname)
    print 'Done:', p.name, p.pid
    sys.stdout.flush()
    driver.quit()


if __name__ == '__main__':
    jobs = []
    for x in range(5):
        j = multiprocessing.Process(target=getn, args=('http://www.aalto.fi/fi/', 3))
        jobs.append(j)
        j.start()
    
    for job in jobs:
        job.join()
