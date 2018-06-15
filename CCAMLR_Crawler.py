# -*- coding: utf-8 -*-
"""
Spyder Editor

"""

from bs4 import BeautifulSoup
import re
import requests
import time
# 需要额外安装pymysql库
import pymysql


def getHTMLText(url, kv):
    try:
        req = requests.get(url, params=kv)
        # 记录报文的状态码，以检查是否能正常连接
        req.raise_for_status() 
        req.encoding = req.apparent_encoding
        return req.text
    except:
        return ""

def getNewsData(url, kv, db, successCnt):
    # 获取HTML页面
    html = getHTMLText(url, kv)
    # 解析HTML页面
    soup = BeautifulSoup(html, "html.parser")
    # 从<article id="main-content">标签中查找新闻列表
    articlesoup = soup.find('article', {'id':'main-content'})
    # 正则表达式
    pattern = re.compile(r'views-row.*')
    # 从<div class="view-content">标签中查找需要的新闻内容
    viewsoup = articlesoup.find('div', {'class':'view-content'})
    # 遍历一个网页中的新闻
    for view in viewsoup.find_all('div', {'class':pattern}):
        try:
            # 观察网页结构得知，新闻链接地址都放在<h2 class="field-content">中的<a href>标签中
            # 先查找所有的<h2 class="field-content">标签
            h2 = view.find('h2', {'class':'field-content'})
            # 从<h2 class="field-content">标签中找到<a>标签
            a = h2.find('a')
            # 找到<a>标签的"href"属性
            url = a.attrs['href']
            # 提取新闻链接
            title = a.string
            # 从<div class="news-body">找到新闻时间标签
            dateTag = view.find_all('div', {'class':'news-body'})[-1]
            # 获得新闻时间
            date = dateTag.string
            #print('Title: ' + title)
            #print('URL: ' + url)
            #print('Date: ' + date)
            # 执行向数据库插入语句的函数，返回插入成功或失败，并更新successCnt值
            successCnt += insertToDB(db, kv, title, url, date)
        except:
            continue
    return successCnt

def getPageNumber(url, kv):
    # 获取HTML页面
    html = getHTMLText(url, kv)
    # 解析HTML页面
    soup = BeautifulSoup(html, "html.parser")
    # 从<li class="pager-last last">标签中查找最后一页新闻的链接
    target = soup.find('li', {'class':'pager-last last'})
    # 从<li class="pager-last last">标签中找到<a>标签
    a = target.find('a')
    # 找到<a>标签的"href"属性
    url = a.attrs['href']
    # 提取链接中的数字集合
    number = re.findall('\d+', url)
    # 提取第一个（唯一一个）数字
    pageCnt = number[0]
    #print(pageCnt)
    return int(pageCnt)


def insertToDB(db, kv, title, url, date):
    # 主机地址
    host = 'https://www.ccamlr.org'
    # 要爬取的新闻链接的完整地址
    url = host + url
    # 获取HTML页面
    html = getHTMLText(url, kv)
    # 解析HTML页面
    soup = BeautifulSoup(html, "html.parser")
    # 从<div class="field-item even">标签中查找最后一页新闻的链接
    content = ""
    for paras in soup.find_all('div', {'class':'field-item even'}):
        try:
            for p in paras.find_all('p'):
                #print(p.get_text())
                content = content + pymysql.escape_string(p.get_text()) + "\n"
        except:
            pass
    #print(content)
    # 使用cursor()方法获取操作游标
    cur = db.cursor()
    # 记录SQL插入语句
    insertSql = 'insert into News (newsTitle, newsURL, newsDate, newsContent) values("{0}", "{1}", "{2}", "{3}");'.format(title, url, date, content)
    #print(insertSql)
    try:
        # 执行SQL插入语句
        cur.execute(insertSql)
        # 向数据库提交
        db.commit()
        # 返回成功插入1条新数据
        return 1
    except Exception as e:
        # 出现错误，回滚操作
        db.rollback()
        # 返回插入失败
        # print(str(e))
        return 0
    finally:
        # 关闭操作游标
        cur.close()

# 爬虫程序主函数
def crawler():
    print('Start crawling...')
    # 记录开始时间
    startTime = time.time()
    # 主机地址
    host = 'https://www.ccamlr.org'
    # 要爬取的新闻链接的完整地址
    url = host + '/en/organisation/ccamlr-news'
    kv = {}
    # 记录成功插入数据库的记录数量
    successCnt = 0
    print('Request pages messages from target website...')
    # 记录爬取的页面数量
    pageCnt = getPageNumber(url, kv)
    print('Connect MySQL database...')
    
    # 连接数据库
    try:
        # Python3默认编码是utf8，因此mysql需指定编码方式为utf8，否则默认是编码是Latin，出现中文时会乱码
        db = pymysql.connect('localhost', 'root', '', 'CCAMLRNews', use_unicode=True, charset="utf8")
        print('Successfully connect MySQL database!')
        print('Crawling, please wait...')
        # 循环，一个一个网页顺序抓取
        for i in range(pageCnt + 1):
            kv['page'] = i
            successCnt = getNewsData(url, kv, db, successCnt)
        # 关闭数据库
        db.close()
        print('Crawling finished!')
        print('')
        print('Successfully update {0} records'.format(str(successCnt)))
    # 异常处理，返回数据库连接失败的报错
    except Exception as e:
        print('Connect failed! Error message: ' + str(e))     
    
    # 记录结束时间
    endTime = time.time()
    print('Time spent on crawling and updating: {0} seconds.'.format(endTime-startTime))

# 执行程序的主函数
crawler()
