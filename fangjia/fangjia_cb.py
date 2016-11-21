# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 16:23:05 2016

@author: warning
"""

from bs4 import BeautifulSoup as BS
import urlparse
import pandas as pd

def get_tags(html):
    soup = BS(html, 'lxml')
    # 获取列表
    li_list = soup.find_all('li', attrs={'name':'__page_click_area'})
    tags_list = []
    for li in li_list:
        # title
        h_name = li.find('a', attrs={'class':'h_name'})
        title = h_name.attrs['title']
        # id
        id = li.attrs['id']
        # address
        span_address = li.find('span', attrs={'class':'address'})
        address = span_address.text
        # hotel
        hotel = span_address.find('em').text
        # attribute
        span_attribute = li.find('span', attrs={'class':'attribute'})
        attribute = span_attribute.text
        # price
        span_x = li.find('span', attrs={'class':'xq_aprice xq_esf_width'})
        pps = span_x.text
        tags_list.append([id, title, hotel, address, attribute, pps])
    data = pd.DataFrame(tags_list)   
    return data

class FangjiaCallback:
    def __call__(self, url, html):
        soup = BS(html, 'lxml')
        nextt = soup.find('a', attrs={'class':'next'})
        next_url = None
        if nextt:
            next_url = nextt.attrs['href']
            next_url = urlparse.urljoin(url, next_url)
            return next_url
