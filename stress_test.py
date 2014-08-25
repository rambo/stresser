#!/usr/bin/env python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import selenium.common.exceptions as seleniumexceptions
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
import time, datetime
import multiprocessing
import sys,os

REMOTE='http://10.211.55.14:4444/wd/hub'


# from http://stackoverflow.com/questions/11360854/right-way-to-test-page-load-time-in-selenium
def get_performance(driver):
    return driver.execute_script("""var performance = window.performance || {};
var timings = performance.timing || {};
return timings;""")

def getn(url, n):
    import atexit
    p = multiprocessing.current_process()
    print 'Starting:', p.name, p.pid
    sys.stdout.flush()
    driver = None
    try:
        driver = webdriver.Remote(
                        desired_capabilities=DesiredCapabilities.FIREFOX,
                        command_executor=REMOTE
        )
        # This doesn't seem to work with multiprocessing...
        atexit.register(driver.quit)
        driver.implicitly_wait(30)
        driver.maximize_window()
        print 'Ready:', p.name, p.pid
        sys.stdout.flush()
        for i in range(n):
            b = time.time()
            driver.get(url)
            took = time.time() - b
            print "pid %d, time %f: got %s in %f seconds" % (p.pid, time.time(), url, took)
            sys.stdout.flush()
            perf = get_performance(driver)
            ttfb = perf[u'responseStart'] - perf[u'fetchStart']
            ttlb = perf[u'responseEnd'] - perf[u'fetchStart']
            ttrdy = perf[u'loadEventEnd'] - perf[u'fetchStart']
            rendertime = perf[u'loadEventEnd'] - perf[u'responseEnd']
            print "pid %d, time %f: %s ttfb=%d ttlb=%d ttrdy=%d rendertime=%d" % (p.pid, time.time(), url, ttfb, ttlb, ttrdy, rendertime)
            b = time.time()
            fname = "%d_%s.png" % (p.pid,datetime.datetime.now().isoformat())
            took = time.time() - b
            driver.get_screenshot_as_file(fname)
            #print "pid %d, time %f: dumped %s in %f seconds" % (p.pid, time.time(), fname, took)
            #sys.stdout.flush()
    
        # Stupider wait (it sorta works (at least on FF, but then I get errors from WebDriverWait...)
        #time.sleep(15)
        #fname = "%d_%s.png" % (p.pid,datetime.datetime.now().isoformat())
        #driver.get_screenshot_as_file(fname)
    
        # Wait for slide change and grab second screenshot
        try:
            WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.carousel-box .box-content:nth-child(2)')))
            fname = "%d_%s.png" % (p.pid,datetime.datetime.now().isoformat())
            driver.get_screenshot_as_file(fname)
        except seleniumexceptions.TimeoutException,e:
            print "pid %d, time %f: TimeOut when waiting for element!" % (p.pid, time.time())
            sys.stdout.flush()
            fname = "%d_%s_notfound.png" % (p.pid,datetime.datetime.now().isoformat())
            driver.get_screenshot_as_file(fname)

    except seleniumexceptions.WebDriverException, e:
        print "pid %d, time %f: EXCEPTION: %s" % (p.pid, time.time(), e)
        sys.stdout.flush()
    finally:
        print 'Done:', p.name, p.pid
        sys.stdout.flush()
        if driver:
            driver.quit()


if __name__ == '__main__':
    jobs = []
    for x in range(5):
        j = multiprocessing.Process(target=getn, args=('http://www.aalto.fi/fi/', 10))
        jobs.append(j)
        j.start()
    
    for job in jobs:
        job.join()
