# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 16:32:12 2016

@author: warning
"""

import time
import threading
import urlparse
from downloader import Downloader
from fangjia_cb import get_tags

SLEEP_TIME = 1

def thread_crawler(seed_urls, delay=5, cache=None, scrape_callback=None, user_agent='wswp', proxies=None, num_retries=1, max_threads=10, timeout=60):
    """Crawl this website in multiple threads
    """
    # the queue of URL's that still need to be crawled
    #crawl_queue = Queue.deque([seed_url])
    crawl_queue = seed_urls
    data_list = []
    # the URL's that have been seen 
    seen = set(seed_urls)
    D = Downloader(cache=cache, delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, timeout=timeout)

    def process_queue():
        while True:
            try:
                url = crawl_queue.pop()
            except IndexError:
                # crawl queue is empty
                break
            else:
                html = D(url)
                data = get_tags(html)
                data_list.append(data) 
                if scrape_callback:
                    try:
                        next_link = scrape_callback(url, html) or []
                    except Exception as e:
                        print 'Error in callback for: {}: {}'.format(url, e)
                    else:
                        if next_link and (next_link not in seen):
                            seen.add(next_link)
                            # add this new link to queue
                            crawl_queue.append(next_link)


    # wait for all download threads to finish
    threads = []
    while threads or crawl_queue:
        # the crawl is still active
        for thread in threads:
            if not thread.is_alive():
                # remove the stopped threads
                threads.remove(thread)
        while len(threads) < max_threads and crawl_queue:
            # can start some more threads
            thread = threading.Thread(target=process_queue)
            thread.setDaemon(True) # set daemon so main thread can exit when receives ctrl-c
            thread.start()
            threads.append(thread)
        # all threads have been processed
        # sleep temporarily so CPU can focus execution on other threads
        time.sleep(SLEEP_TIME)
        
    return data_list
