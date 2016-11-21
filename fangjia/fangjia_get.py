# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 11:40:37 2016

@author: warning
"""
import pandas as pd
import numpy as np
import cPickle
import re

def extract_title(t):
    #t = t.decode('utf-8')
    t = t.strip()
    return t.replace(u'，', u' ')
    
def extract_hotel(h):
    #h = h.decode('utf-8')
    patten = re.compile(u'【(.*)-(.*)】')
    m = re.match(patten, h)
    if m:
        return m.groups(0)
    else:
        return (np.NaN, np.NaN)
        
def extract_addr(addr):
    #addr = addr.decode('utf-8')
    patten = re.compile(u'\n.*\n(.*)\n')
    m = re.match(patten, addr)
    if m:
        return m.groups(0)[0]
    else:
        return np.NaN
        
def extract_attrs(attr):
    #attr = attr.decode('utf-8')
    patten = re.compile(u'\n面积：(\d+)平米，房型：(.*)，楼层：(.*)\n')
    m = re.match(patten, attr)
    if m:
        return m.groups(0)
    else:
        patten2 = u'\n面积：(\d+)平米，房型：(.*)\n'
        m = re.match(patten2, attr)
        if m:
            res = [m.groups(0)[0], m.groups(0)[1], np.NaN]
        else:
            res = [np.NaN, np.NaN, np.NaN]
        return res
    
def extract_pps(pps):
    #pps = pps.decode('utf-8')
    patten = re.compile(u'\n(\d+)万(\d+)元/㎡(.*)\n')
    m = re.match(patten, pps)
    return m.groups(0)
    
if __name__ == '__main__':
    with open('fangjia-all.pkl', 'rb') as fp:
        data = cPickle.load(fp)
        
    titles = []
    hotels = []
    addrs = []
    attrs = []
    ppss = []
    
    for t in data.title:
        titles.append(extract_title(t))
    for h in data.hotel:
        hotels.append(extract_hotel(h))
    for addr in data.address:
        addrs.append(extract_addr(addr))
    for attr in data.attribute:
        #print attr
        attrs.append(extract_attrs(attr))
    for pps in data.pps:
        ppss.append(extract_pps(pps))
    
    titles = pd.DataFrame(titles, columns=[u'标题'])
    hotels = pd.DataFrame(hotels, columns=[u'区域', u'楼盘'])
    addrs = pd.DataFrame(addrs, columns=[u'地址'])
    attrs = pd.DataFrame(attrs, columns=[u'面积', u'房型', u'楼层'])
    ppss = pd.DataFrame(ppss, columns=[u'总价', u'均价', u'来源'])
    
    fetched_data = pd.concat([hotels, addrs, titles, attrs, ppss], axis=1, ignore_index=True)
    fetched_data.columns = [u'区域', u'楼盘', u'地址', u'标题', u'面积', u'房型',
                            u'楼层', u'总价', u'均价', u'来源']
    
