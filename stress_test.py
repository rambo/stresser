#!/usr/bin/python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import *
import atexit

REMOTE='http://10.211.55.14:4444/wd/hub'

ffdriver = webdriver.Remote(
                desired_capabilities=DesiredCapabilities.FIREFOX,
                command_executor=REMOTE
)
atexit.register(ffdriver.quit)
