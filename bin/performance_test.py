#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This script will take a file with URLs (one per line) and will spawn a fresh firefox (with empty cache) to fetch each URL and record some performance data in CSV format"""
from __future__ import with_statement
from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import selenium.common.exceptions as seleniumexceptions
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
import time, datetime
import json
import multiprocessing
import sys,os

#REMOTE='http://10.211.55.14:4444/wd/hub'
REMOTE='http://127.0.0.1:4444/wd/hub'
CAPS=DesiredCapabilities.FIREFOX
#CAPS=DesiredCapabilities.CHROME
#driver = webdriver.Remote(desired_capabilities=DesiredCapabilities.FIREFOX, command_executor=REMOTE)

# from http://stackoverflow.com/questions/11360854/right-way-to-test-page-load-time-in-selenium
def get_performance(driver):
    return driver.execute_script("""var performance = window.performance || {};
var timings = performance.timing || {};
return timings;""")

def getn(url):
    sys.stdout.flush()
    driver = None
    try:
        driver = webdriver.Remote(
                        desired_capabilities=CAPS,
                        command_executor=REMOTE
        )
        driver.implicitly_wait(30)
        driver.maximize_window()
        b = time.time()
        driver.get(url)
        took = time.time() - b
        perf = get_performance(driver)
        ttfb = perf[u'responseStart'] - perf[u'fetchStart']
        ttlb = perf[u'responseEnd'] - perf[u'fetchStart']
        ttrdy = perf[u'loadEventEnd'] - perf[u'fetchStart']
        rendertime = perf[u'domContentLoadedEventEnd'] - perf[u'responseEnd']
        loadtime =  perf[u'domContentLoadedEventStart'] - perf[u'fetchStart']
        timestamp = datetime.datetime.now()
        print(""""%s";"%s";%d;%d;%d;%d;%d;"%s";""" % (timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:23], url, ttfb, ttlb, ttrdy, loadtime, rendertime, json.dumps(perf)))
        sys.stdout.flush()

    except seleniumexceptions.WebDriverException, e:
        print("%f: EXCEPTION: %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:23], e), file=sys.stderr)
        sys.stdout.flush()
    finally:
        sys.stdout.flush()
        if driver:
            driver.quit()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage performance_test.py file_with_urls [num_runs]\n");
        sys.exit(1)

    num_runs = 1
    if len(sys.argv) >= 3:
        num_runs = int(sys.argv[2])

    with open(sys.argv[1]) as urlsfile:
        print(""""timestamp";"url";"ttfb";"ttlb";"ttrdy";"loading time";"rendertime";"Full performance JSON";""");
        for x in range(num_runs):
            urlsfile.seek(0)
            for line in urlsfile:
                url = line.strip()
                if not url:
                    continue
                getn(url)

