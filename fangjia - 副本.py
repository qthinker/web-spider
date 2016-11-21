# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 21:04:12 2016

@author: warning
"""

import urllib2 
import urlparse
#import time
from bs4 import BeautifulSoup as BS
from multiprocessing import Pool
import re
import datetime
import socket
import copy
import pandas as pd


# 获取html
def download(url, user_agent='wswp', num_retries=2):
    print 'downloading:%s' % url
    headers = {'User-agent': user_agent}
    request = urllib2.Request(url, headers=headers)
    try:
        html = urllib2.urlopen(request).read().decode('utf-8')
    except urllib2.URLError as e:
        print 'download error:%s' % e.reason
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return download(url, user_agent, num_retries-1)
    except socket.timeout as e:
        print 'socket timeout %s' % url
    return html

# 获取查询关键词dict
def get_search(page, key):
    soup = BS(page, 'lxml')
    search_list = soup.find_all(href=re.compile(key), target='')
    search_dict = {}
    for i in range(len(search_list)):
        soup = BS(str(search_list[i]), 'lxml')
        key = soup.select('a')[0].get_text()
        value = soup.a.attrs['href']
        search_dict[key] = value
    return search_dict


# 获取房源信息列表(嵌套字典遍历)
def get_info_list(search_dict, layer, tmp_list, search_list):
    layer += 1  # 设置字典层级
    for i in range(len(search_dict)):
        tmp_key = list(search_dict.keys())[i]  # 提取当前字典层级key
        tmp_list.append(tmp_key)   # 将当前key值作为索引添加至tmp_list
        tmp_value = search_dict[tmp_key]
        if isinstance(tmp_value, str):   # 当键值为url时
            tmp_list.append(tmp_value)   # 将url添加至tmp_list
            search_list.append(copy.deepcopy(tmp_list))   # 将tmp_list索引url添加至search_list
            tmp_list = tmp_list[:layer]  # 根据层级保留索引
        elif tmp_value == '':   # 键值为空时跳过
            layer -= 2           # 跳出键值层级
            tmp_list = tmp_list[:layer]   # 根据层级保留索引
        else:
            get_info_list(tmp_value, layer, tmp_list, search_list)  # 当键值为列表时，迭代遍历
            tmp_list = tmp_list[:layer]
    return search_list

def get_data(url):
    html = download(url)
    if not html:
        return None
    soup = BS(html, 'lxml')
    # 获取列表
    li_list = soup.find_all('li', attrs={'name':'__page_click_area'})
    titles = []
    ids = []
    addrs = []
    hotels = []
    attrs = []
    ppss = []
    for li in li_list:
        # title
        h_name = li.find('a', attrs={'class':'h_name'})
        title = h_name.attrs['title']
        titles.append(title)
        # id
        id = li.attrs['id']
        ids.append(id)
        # address
        span_address = li.find('span', attrs={'class':'address'})
        address = span_address.text
        addrs.append(address)
        # hotel
        hotel = span_address.find('em').text
        hotels.append(hotel)
        # attribute
        span_attribute = li.find('span', attrs={'class':'attribute'})
        attribute = span_attribute.text
        attrs.append(attribute)
        # price
        span_x = li.find('span', attrs={'class':'xq_aprice xq_esf_width'})
        pps = span_x.text
        ppss.append(pps)
    data = pd.DataFrame([ids, titles, hotels, addrs, attrs, ppss])   
    nextt = soup.find('a', attrs={'class':'next'})
    next_url = None
    if nextt:
        next_url = nextt.attrs['href']
        next_url = urlparse.urljoin(url, next_url)
        print 'has next url %s ' % next_url
    return (data.T, next_url)
    
def crawler(seed_url, i):
    print 'processing %d' % i
    data_list = []
    url = seed_url
    while True:
        data, url = get_data(url)
        data_list.append(data)
        if not url:
            break
    return pd.concat(data_list, ignore_index=True)

if __name__ == '__main__':
    starttime = datetime.datetime.now()
    base_url = r'http://cd.fangjia.com/ershoufang/'
    search_list = []  # 房源信息url列表
    tmp_list = []  # 房源信息url缓存列表
    layer = -1
    file_name = 'fangjia.csv'
    socket.setdefaulttimeout(10)  # 设置超时
    # 一级筛选
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
    # set multiprocess
    p = Pool(4)
    result = []
    urls = [url[-1] for url in fin_info_list[:4]]
    for i, url in enumerate(urls):
        result.append(p.apply_async(crawler, args=[url, i]))
    p.close()
    p.join()
    blocks = []
    for blk in result:
        blocks.append(blk.get())
    data = pd.concat(blocks, ignore_index=True)
    data.columns = ['id', 'title', 'hotel', 'address', 'attribute', 'pps']
    data.to_csv(file_name, encoding='utf-8')
    # compute time    
    endtime = datetime.datetime.now()
    time = (endtime - starttime).seconds
    print u'总共用时：%s s' % time