#!/usr/bin/env python
#python 3

from urllib import request
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
import time
import multiprocessing

headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}


def get_web_content_gbk(url):
    req=request.Request(url,headers=headers)
    response=request.urlopen(req)
    html=response.read()
    result=html.decode('gbk')
    return result

def get_web_content_utf8(url):
    req=request.Request(url,headers=headers)
    response=request.urlopen(req)
    html=response.read()
    result=html.decode('utf-8')
    return result

def get_web_table(url,tr_class):
    # for pages from city to villages, 2 columns on page. For the deepest page with 3 columns, use get_final_table()
    final=[]
    result=get_web_content_gbk(url)
    soup=BeautifulSoup(result,features="lxml")
    trs=soup.find_all('tr',attrs={'class':tr_class})
    for tr in trs:
        tds=tr.find_all('td')
        code=tds[0].string
        name=tds[1].string
        if tds[0].find('a') != None:
            link=urljoin(url,tds[0].find('a').attrs['href'])
        else:
            link=None 
        final.append((link,code,name))
    return final 

def get_final_table(url,tr_class):
    # only for the deepest page, 3 columns
    final=[]
    result=get_web_content_gbk(url)
    soup=BeautifulSoup(result,features="lxml")
    trs=soup.find_all('tr',attrs={'class':tr_class})
    for tr in trs:
        tds=tr.find_all('td')
        code=tds[0].string
        classify=tds[1].string
        name=tds[2].string 
        final.append((code,classify,name))
    return final 

def main(base_url,start=1):
    # url is the main entrance with links to every provinces
    url=base_url+'index.html'
    result=get_web_content_gbk(url)

    #find all 31 provinces, return a 2-dimension list (link,province_name)
    provinces=re.findall(r"<a href='(\d\d.html)'>(.*?)<br/></a>",result)

    #for all provinces, generate a total city list, 3-dimension list (link, city_number,city_name), store as a dictionary
    all_city_info={}
    i=1
    print("=== Get city info from provinces ===")
    for province in provinces:
        url=urljoin(url,province[0])
        #result=get_web_content_gbk(url)
        #citys=re.findall(r"<td><a href='(\d\d/\d\d\d\d.html)'>(\d*?)</a></td><td><a href='\d\d/\d\d\d\d.html'>(.*?)</a></td>",result)
        temp=get_web_table(url,'citytr') 
        all_city_info[province[1]]=temp  
        print("{} Done![{}/{}]".format(province[1],i,len(provinces)))
        i=i+1
        #if i == 6:  # testing purpose
        #    break
    print("=== All cities done ===")
    time.sleep(1)

    #for all cities, generate a total county list, 3-dimension list (link, county_number, county_name), store as a dictionary
    print("=== Write province info to file ===")
    m=1
    print("Start Doanload from province number: {}".format(start))
    time.sleep(2)
    for cities in all_city_info.items():
        #print("=== {} Start ===".format(cities[0]))
        if m < start:
            m=m+1
            continue 
        else:
            write_city_info(cities[0],cities[1])
            m=m+1
    time.sleep(1)
    print("=== All Done ===")


def write_city_info(province,city_info):
    # city_info is a 3-dimension list
    #for all cities, generate a total county list, 3-dimension list (link, county_number, county_name), store as a dictionary
    n=1
    print("=== {} Start ===".format(province))
    to_print=[]
    for city in city_info:
        if city[0] == None:
            to_print.append((city[1],province,city[2],'','',''))
            print("{} {} {} {} {} {} {}".format(city[1],'',province,city[2],'','',''))
            continue
        else:
            towns=get_web_table(city[0],'countytr')
            for town in towns:
                if town[0] == None:
                    to_print.append((town[1],'',province,city[2],town[2],'',''))
                    print("{} {} {} {} {} {} {}".format(town[1],'',province,city[2],town[2],'',''))
                    continue
                else:
                    villages=get_web_table(town[0],'towntr')
                    for village in villages:
                        if village[0] == None:
                            to_print.append((village[1],'',province,city[2],town[2],village[2],''))
                            print("{} {} {} {} {} {} {}".format(village[1],'',province,city[2],town[2],village[2],''))
                            continue
                        else:
                            offices=get_final_table(village[0],'villagetr')
                            for office in offices:
                                to_print.append((office[0],office[1],province,city[2],town[2],village[2],office[2]))
                                print("{} {} {} {} {} {} {}".format(office[0],office[1],province,city[2],town[2],village[2],office[2]))
        print("{}-{} Done! [{}:{}/{}]".format(province,city,province,n,len(city_info)))
        n=n+1
    print("=== {} Done! ===".format(province))
    filename="{}.txt".format(province)
    with open(filename,'w') as f:
        for item in to_print:
            f.write(item[0]+' '+item[1]+' '+item[2]+' '+item[3]+' '+item[4]+' '+item[5]+' '+item[6]+'\n')

base_url='http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/'
# start from the 1st province, unless a start number is specified
main(base_url,4)

# test only
#url='http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/42/4201.html'
#result=get_web_table(url,'countytr')
#print(result)
