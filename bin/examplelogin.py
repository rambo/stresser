import os

USERNAME=os.environ.get('PERF_TEST_USER')
PASSWORD=os.environ.get('PERF_TEST_USER_PASSWD')

class loginhandler:
    def __init__(self, webdriver):
        self.driver = webdriver
    
    def login(self):
        self.driver.get('https://www.example.com/login')
        self.driver.find_element_by_id('username').send_keys(USERNAME)
        self.driver.find_element_by_id('password').send_keys(PASSWORD)
        self.driver.find_element_by_id('login').submit()
