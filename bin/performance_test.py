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
import sys,os,atexit
try:
    import urlparse
except ImportError,e:
    import urllib.parse as urlparse

#REMOTE='http://10.211.55.14:4444/wd/hub'
REMOTE='http://127.0.0.1:4444/wd/hub'
CAPS=DesiredCapabilities.FIREFOX
#CAPS=DesiredCapabilities.CHROME
#driver = webdriver.Remote(desired_capabilities=DesiredCapabilities.FIREFOX, command_executor=REMOTE)

# from http://stackoverflow.com/questions/11360854/right-way-to-test-page-load-time-in-selenium
def get_performance(driver):
    return DRIVER.execute_script("""var performance = window.performance || {};
var timings = performance.timing || {};
return timings;""")

DRIVER = None

def getn(url):
    sys.stdout.flush()
    driver = None
    try:
        b = time.time()
        DRIVER.get(url)
        took = time.time() - b
        perf = get_performance(driver)
        # This doesn't seem to affect the weird result for ttrdy the first time we hit the redirects
        if perf[u'redirectEnd']:
            perf_start_ts = perf[u'redirectEnd']
        else:
            perf_start_ts = perf[u'fetchStart']
        ttfb = perf[u'responseStart'] - perf_start_ts
        ttlb = perf[u'responseEnd'] - perf_start_ts
        ttrdy = perf[u'loadEventEnd'] - perf_start_ts
        rendertime = perf[u'domContentLoadedEventEnd'] - perf[u'responseEnd']
        loadtime =  perf[u'domContentLoadedEventStart'] - perf_start_ts
        timestamp = datetime.datetime.now()
        print(""""%s";"%s";%d;%d;%d;%d;%d;"%s";""" % (timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:23], url, ttfb, ttlb, ttrdy, loadtime, rendertime, json.dumps(perf)))
        #DRIVER.get_screenshot_as_file("%s.png" % (timestamp.strftime("%Y%m%d_%H%M%S_%f")[:23]))
        sys.stdout.flush()

    except seleniumexceptions.WebDriverException, e:
        print("%s: EXCEPTION: %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:23], e), file=sys.stderr)
        sys.stdout.flush()
    finally:
        sys.stdout.flush()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage performance_test.py file_with_urls [num_runs] [login_handler_module]\n");
        sys.exit(1)

    num_runs = 1
    if len(sys.argv) >= 3:
        num_runs = int(sys.argv[2])

    socks_proxy = os.environ.get('SOCKS_PROXY')
    if not socks_proxy:
        DRIVER = webdriver.Remote(
            desired_capabilities=CAPS,
            command_executor=REMOTE
        )
    elif CAPS == DesiredCapabilities.FIREFOX:
        ffprofile = webdriver.FirefoxProfile()
        ffprofile.set_preference('network.proxy.type', 1)
        ffprofile.set_preference('network.proxy.socks', socks_proxy.split(':')[0])
        ffprofile.set_preference('network.proxy.socks_port', int(socks_proxy.split(':')[1]))
        DRIVER = webdriver.Remote(
            desired_capabilities=CAPS,
            browser_profile = ffprofile,
            command_executor=REMOTE
        )
    else:
        raise Exception("Do not know how to set proxy for %s" % CAPS)

    atexit.register(DRIVER.quit)
    DRIVER.implicitly_wait(30)
    #DRIVER.maximize_window()
    DRIVER.set_window_size(1280, 1024)

    # If we have login_handler_module specified, use it
    if len(sys.argv) >= 4:
        import importlib
        m = importlib.import_module(sys.argv[3])
        h = m.loginhandler(DRIVER)
        h.login()

    # Check if we want to set the xdebug profiling cookie
    profile_url = os.environ.get('XDEBUG_PROFILE')
    if profile_url:
        DRIVER.get(profile_url)
        DRIVER.add_cookie({
            'name': 'XDEBUG_PROFILE',
            'value': '1',
            'paht': '/',
            'domain': urlparse.urlparse(profile_url).netloc
        })

    # Go trhough the urls file line by line
    with open(sys.argv[1]) as urlsfile:
        print(""""timestamp";"url";"ttfb";"ttlb";"ttrdy";"loading time";"rendertime";"Full performance JSON";""");
        for x in range(num_runs):
            urlsfile.seek(0)
            for line in urlsfile:
                url = line.strip()
                if (   not url
                    or url.startswith('#')):
                    continue
                getn(url)

    # atexit will handle this
    #DRIVER.quit()

