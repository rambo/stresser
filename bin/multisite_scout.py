#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Takes a base url from cli, walks all links under the same tree recursively, returns list of successfully fetched urls"""
from __future__ import with_statement
from __future__ import print_function
import scout
import multiprocessing


class mpjobmanager(scout.jobmanager):

    def run(self, fetched_urls):
        super(mpjobmanager, self).run()
        fetched_urls += self.fetched_urls


if __name__ == '__main__':
    import os,sys
    if len(sys.argv) < 2:
        print("Usage: multisite_scout urls.txt [css_selector]\n")
        sys.exit(1)

    manager =  multiprocessing.Manager()
    all_urls = manager.list()
    processes = []
    with open(sys.argv[1]) as f:
        for urlb in f:
            url = urlb.strip()
            # Skip empty ones
            if not url:
                continue
            # Also skip "commented out" lines
            if url.startswith('#'):
                continue
            jm = mpjobmanager(url)
            if len(sys.argv) >= 3:
                jm.fetcher.css_selector = sys.argv[2]
            
            p = multiprocessing.Process(target=jm.run, args=(all_urls,))
            p.start()
            processes.append(p)

    # TODO: handle crtl-c gracefully.    
    for p in processes:
        p.join(30)

    print("\n=== Succesfully fetched URLS ===")
    for url in all_urls:
        print(url)
