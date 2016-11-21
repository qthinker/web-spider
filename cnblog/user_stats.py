# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 17:41:45 2016

@author: warning
"""

from bs4 import BeautifulSoup as BS
from downloader import Downloader
from mongo_cache import MongoCache

test_url = 'http://www.cnblogs.com/skyme/'
test_url2 = 'http://www.cnblogs.com/mvc/blog/news.aspx?blogApp=yexiaochai'

def get_user_stats_urls(D):
    user_stats_url = 'http://www.cnblogs.com/aggsite/UserStats'
    html = D(user_stats_url)
    soup = BS(html, 'lxml')
    div = soup.find('div', attrs={'id':'blogger_list'})
    a_list = div.find_all('a')
    res = {}
    for a in a_list[:100]:
        res[a.text] = a.attrs['href']
    return res
    
def get_tags_level_1(url, D):
    url_mode = 'http://www.cnblogs.com/mvc/blog/news.aspx?blogApp=%s'
    user_id = url.split('/')[-2]
    new_url = url_mode % user_id
    html = D(new_url)
    try:
        soup = BS(html)
        div = soup.find('div', attrs={'id':'profile_block'})
        a_list = div.find_all('a')
        res = [a.text for a in a_list]
    except:
        print 'get tags error'
        res = None
    return res
    
if __name__ == '__main__':
    cache = MongoCache()
    D = Downloader(cache=cache, delay=1)
    seed_urls = get_user_stats_urls(D)
    user_profile_list = []
    for name in seed_urls:
        url = seed_urls[name]
        tags = get_tags_level_1(url, D)
        if tags:
            user_profile_list.append(tags)
    