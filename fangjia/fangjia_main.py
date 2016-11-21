# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 16:48:28 2016

@author: warning
"""
import datetime
from fangjia_thread_crawler import thread_crawler
from fangjia_cb import FangjiaCallback
from mongo_cache import MongoCache
from downloader import Downloader
from fangjia2 import get_search
from fangjia2 import get_info_list
from fangjia2 import download
import pandas as pd
import cPickle
import os

if __name__ == '__main__':
    # get the seed_urls
    starttime = datetime.datetime.now()
    seed_urls = []
    cache = MongoCache() # cache all pages
    if os.path.exists('seed_urls.pkl'):
        with open('seed_urls.pkl', 'rb') as fp:
            seed_urls = cPickle.load(fp)
    else:
        base_url = r'http://cd.fangjia.com/ershoufang/'
        search_list = []  # 房源信息url列表
        tmp_list = []  # 房源信息url缓存列表
        layer = -1
        # 一级筛选
        #D = Downloader(cache=cache)
        page = download(base_url)
        search_dict = get_search(page, 'r-')
        # 二级筛选
        for k in search_dict:
            print u'****************一级抓取：正在抓取【%s】***************' % k
            url = search_dict[k]
            second_page = download(url)
            second_search_dict = get_search(second_page, 'b-')
            search_dict[k] = second_search_dict
        # get seed_url list
        fin_info_list = get_info_list(search_dict, layer, tmp_list, search_list)
        seed_urls = [x[-1] for x in fin_info_list]
        with open('seed_urls.pkl', 'wb') as fp:
            cPickle.dump(seed_urls, fp)
    # middle time
    mid_time = datetime.datetime.now()
    print 'get seed_urls use time : %s s' % (mid_time - starttime)
    # start crawler
    max_thread = 8  
    callback = FangjiaCallback()
    data_list = thread_crawler(seed_urls,
                   delay=0.1,
                   cache=cache, 
                   scrape_callback=callback,
                   max_threads=max_thread)
    data = pd.concat(data_list, ignore_index=True)
    data.columns = ['id', 'title', 'hotel', 'address', 'attribute', 'pps']
    with open('fangjia-all.pkl', 'wb') as fp:
        cPickle.dump(data, fp)
    data.to_csv('fangjia-all.csv', encoding='utf-8')
    end_time = datetime.datetime.now()
    print 'all the time %s s' % (end_time - starttime)