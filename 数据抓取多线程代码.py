# -*- coding: utf-8 -*-
"""
Created on Sun Dec 12 18:26:43 2021

@author: 木子津九
"""

import requests
from requests.exceptions import ReadTimeout, ConnectionError, RequestException
import urllib.robotparser
from bs4 import BeautifulSoup
import os
import csv
import time
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver import Chrome
from selenium import webdriver 

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36 Edg/96.0.1054.29'}
domain="http://finance.people.com.cn/"#所有子超链接的根目录
url_0="http://www.people.com.cn/"#网站根目录，其下可以查看Robots协议

def connection(url):#判断网站能否连通，是否存在异常或错误
    try:
        req=requests.get(url,headers=headers,timeout=5)
        #print(req.status_code)
    except ReadTimeout:#超时异常
        print('Timeout')
    except ConnectionError:#连接异常
        #无法访问此页面！
        print('Connection error')
    except RequestException:#请求异常
        print('Error')
    else:
        if req.status_code==200:
            #print("访问正常！")
            return True
        if req.status_code==404:
            print("页面不存在！")
        if req.status_code==403:
            print('页面禁止访问！')

def is_allowed_spider(url_0,url):#基于Robots协议判断网站是否允许爬虫
    rp=urllib.robotparser.RobotFileParser()
    rp.set_url(url_0+"/robots.txt")
    rp.read()   
    useragent='Googlebot'
    if rp.can_fetch(useragent,url):
        #print("允许抓取")
        return True
    else:
        print("不允许抓取")
        return False

def pachong(url):
    #读入cookies文本文件，改写成requests可以识别的格式
    f_cookie=open(r'C:\Users\mzjj\Desktop\cookies.txt','r',encoding='utf8')
    cookies={}
    for line in f_cookie.read().split(';'):
        name,value=line.strip().split('=',1)
        cookies[name]=value
    f_cookie.close()
  
    r=requests.get(url=url,headers=headers,cookies=cookies)
    r.encoding='gb2312'
    html=r.text
    bs=BeautifulSoup(html,'lxml')#利用lxml解析器构造BeautifulSoup解析
    list=bs.find("div",class_="ej_list_box clear").find_all("a")
    url_list=[]
    for i in list:
        href=i.get('href')
        title=i.string
        #print(title)
        if title=='1' or title=='上一页':
            break
        true_href=domain+str(href)
        url_list.append(true_href)#得到子页面链接列表
    r.close()  
    
    for url in url_list: 
        chrome_options = webdriver.ChromeOptions()
        # 使用headless无界面浏览器模式，即不需要打开浏览器
        chrome_options.add_argument('--headless')  # 增加无界面选项
        web=Chrome(options=chrome_options)
        web.get(url)
        html = web.page_source
        
        bs=BeautifulSoup(html,'lxml')       
        title=bs.select('div.col.col-1.fl > h1')[0].text#提取新闻标题
        #print(title)
       
        date_time=bs.select('div.col-1-1.fl')[0].text.split("|")[0].strip()#提取新闻时间
        #print(time)
        
        place=bs.select('div.col-1-1.fl > a')[0].text#提取新闻来源
        #print(place)
        
        contents=bs.select('div.rm_txt_con.cf > p')#提取新闻内容
        text=''
        for i in contents:
            text+=i.text.strip()
        #print(text)
        
        editor=bs.select('div.edit.cf')[0].text.strip("()")#提取责任编辑
        #print(editor)
        
        img=bs.select('div.rm_txt_con.cf > p > img')#提取图片链接
        img_trueh=None
        for i in img:
            img_href=i.get("src")#提取超链接
            img_trueh=domain+img_href
            #print(img_trueh)
            img_name=i.get("desc")#提取图片描述
            #print(img_name)
            img_resq=requests.get(img_trueh)
            path="C:/Users/mzjj/Desktop/img/"+title#以文章标题创建文件夹
            
            if os.path.exists(path)==False:#文章第一张图片，没有新建路径，就新建一个文件夹
                os.makedirs(path)
            if img_name==None: #有图没名字
                img_name=img_href.split("/")[4][:-4]#取超链接尾部作为名字
            with open("C:/Users/mzjj/Desktop/img/"+title+"/"+img_name+".jpg",mode="wb") as f_img:
                f_img.write(img_resq.content)#每张图片名字是该图片的描述文本#下载图片
                
        import re
        video_href=None
        obj=re.compile(r'<video id.*?<source="" src="(?P<video_href>.*?)"',re.S)#预加载正则表达式
        video=obj.finditer(html)#返回迭代器
        for i in video:
            video_href=i.group('video_href')
            #print(video_href)
            #video_name=video_href.split("/")[-1]
            #print(video_name)

                
                
        f=open("xinwen.csv",'a+',newline='',encoding='utf-8')
        csv.writer(f).writerow([title,date_time,place,text,editor,url,img_trueh,video_href])



if __name__ == '__main__':
    start=time.time()
    with ThreadPoolExecutor(4) as t:    #创建线程池          
        f=open("xinwen.csv",'w',newline='',encoding='utf-8')
        csv.writer(f).writerow(["标题","时间","来源","新闻内容","责任编辑","新闻网址","图片链接","视频链接"])
        f.close()   
        for i in range(1,5):
            url=f'http://finance.people.com.cn/GB/70846/index{i}.html'
            if connection(url) and is_allowed_spider(url_0,url):
                t.submit(pachong,url)
    end=time.time()
    duration=end-start
    print(duration)