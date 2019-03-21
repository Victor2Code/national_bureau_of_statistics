#!/usr/bin/env python
#python 3

from urllib import request
from bs4 import BeautifulSoup
import re

def get_region_numbers(base_url):
    # url is the main entrance with links to every provinces
    url=base_url+'index.html'
    response=request.urlopen(url)
    html=response.read()
    result=html.decode('gbk')

    #find all 31 provinces, return a 2-dimension list
    provinces=re.findall(r"<a href='(\d\d.html)'>(.*?)<br/></a>",result)
    
    #for each province, generate a city list 


base_url='http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/'
get_region_numbers(base_url)
