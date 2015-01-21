#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Takes a base url from cli, walks all links under the same tree recursively, returns list of successfully fetched urls"""
from __future__ import with_statement
from __future__ import print_function
import re, urllib2
from bs4 import BeautifulSoup


class jobmanager:
    def __init__(self, entry_url):
        self.job_queue = [entry_url, ]
        self.seen_urls = { entry_url: True }
        self.fetched_urls = []
        self.fetcher = fetcher(entry_url, self)

    def add_to_queue(self, url):
        """Add given URL to job queue unless it has previously been added there already"""
        if self.seen_urls.has_key(url):
            return False
        self.job_queue.append(url)
        self.seen_urls[url] = True
        return True

    def run(self):
        while(len(self.job_queue) > 0):
            url = self.job_queue.pop(0)
            self.fetcher.fetch(url)

class fetcher:
    """This will take a pad URL (under ETHERPAD_BASE) and dump it as HTML, then follow any links to same etherpad server and dump those as well"""
    def __init__(self, base, queuemanager):
        self.BASE_RE = re.compile('^%s.+/$' % base)
        
        # This is just a reference so we can push jobs to the queue
        self.queuemanager = queuemanager

    def fetch(self, url):
        """This will fetch a single url and find any links in it under same tree and add them to the job queue"""
        print("Fetching %s" % url)
        try:
            fp = urllib2.urlopen(url)
        except urllib2.URLError,e:
            print("Failed to fetchs %s: %s" % (url, e))
            return False

        self.queuemanager.fetched_urls.append(url)

        soup = BeautifulSoup(fp)
        recurse_links = soup.find_all('a', href=self.BASE_RE)
        for tag in recurse_links:
            # Doublecheck the url is sane pad
            new_pad_url = tag['href']
            # Add to processing list
            self.queuemanager.add_to_queue(new_pad_url)

if __name__ == '__main__':
    import os,sys
    if len(sys.argv) < 2:
        print("Usage: scout base url\n")
        sys.exit(1)
    jm = jobmanager(sys.argv[1])
    jm.run()
    print("\n=== Succesfully fetched URLS ===")
    for url in jm.fetched_urls:
        print(url)
