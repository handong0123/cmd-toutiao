import hashlib
import json
import os
import queue
import re
import time
import keyboard
import requests
from bs4 import BeautifulSoup

from objects import News

# 数据源url
base_data_url = 'https://www.toutiao.com/api/pc/feed/?category=news_hot&utm_source=toutiao&widen=1&max_behot_time={}&max_behot_time_tmp={}&tadrequire=true&as={}&cp={}'
base_source_url = 'https://www.toutiao.com'

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
}
cookies = {'tt_webid': '6649949084894053895'}  # cookies可从浏览器中查找，为了避免被头条禁止爬虫
max_behot_time = 0  # 默认从0开始，接口返回中获取下一个值

# 已爬取的新闻队列
news_queue = queue.Queue(100);
# 当前新闻
now_news = News("", "", "");


def get_as_cp():
    """ 获取as和cp参数，参考今日头条中的加密js文件：home_4abea46.js"""
    # 获取当前计算机时间
    now = round(time.time())
    # 转换一个整数为16进制字符串
    e = hex(int(now)).upper()[2:]
    # 创建hash对象并返回16进制结果
    a = hashlib.md5()
    a.update(str(int(now)).encode('utf-8'))
    i = a.hexdigest().upper()
    if len(e) != 8:
        return {'as': '479BB4B7254C150', 'cp': '7E0AC8874BB0985'}
    n = i[:5]
    a = i[-5:]
    r = ''
    s = ''
    for i in range(5):
        s += n[i] + e[i]
    for j in range(5):
        r += e[j + 3] + a[j]
    return {'as': 'A1' + s + e[-3:], 'cp': e[0:3] + r + 'E1'}


def get_data(data_url: str):
    """获取接口数据"""
    try:
        r = requests.get(data_url, headers=headers, cookies=cookies)
        return json.loads(r.text)
    except:
        print("get data from toutiao failed")
        raise


def get_html(data_url: str):
    """获取网页数据"""
    try:
        r = requests.get(data_url, headers=headers, cookies=cookies)
        return r.text
    except:
        print("get html from toutiao failed")
        raise


def crawl():
    global max_behot_time
    # 获取as和cp参数值
    ascp = get_as_cp()
    # 格式化url
    data_url = base_data_url.format(max_behot_time, max_behot_time, ascp['as'], ascp['cp'])
    # 获取数据
    http_result = get_data(data_url)
    data = http_result['data']
    for data_index in range(len(data)):
        item = data[data_index]
        title = item['title']
        source = item['source']
        source_url = item['source_url']
        if 'https' not in source_url:
            source_url = base_source_url + source_url
        news = News(title, source, source_url)
        news_queue.put(news)
    # 获取下一个链接的max_behot_time参数的值
    max_behot_time = str(http_result['next']['max_behot_time'])


def clear():
    os.system('cls')


def detail(x):
    event = keyboard.KeyboardEvent('right', 0)
    if x.event_type == 'down' and x.name == event.event_type:
        now_news.print_all()


def content(x):
    event = keyboard.KeyboardEvent('left', 0)
    if x.event_type == 'down' and x.name == event.event_type:
        url = now_news.source_url
        html = get_html(url)
        matcher = re.search(r'content: \'(.*)\'', html)
        if matcher:
            content_str = matcher.group().replace('content: \'', "").replace('\'', "")
            content_html = re.sub(r'(\\u[\s\S]{4})', lambda x: x.group(1).encode("utf-8").decode("unicode-escape"),
                                  content_str)
            content_html = content_html.replace("\&quot;", "\"").replace("&quot;", "").replace("&#x3D;", "=");
            soup = BeautifulSoup(content_html, 'html.parser')
            p_list = soup.find_all('p')
            for p in p_list:
                text = p.get_text()
                if text:
                    print(text)


def next(x):
    event = keyboard.KeyboardEvent('down', 0)
    if x.event_type == 'down' and x.name == event.event_type:
        clear()
        if news_queue.empty():
            crawl()
        global now_news
        now_news = news_queue.get()
        now_news.print_title()


if __name__ == '__main__':
    print("欢迎来到今日头条命令行版，按下键切换新闻，左键查看新闻内容，右键溯源")
    print("请开始您的摸鱼！")
    keyboard.hook(detail)
    keyboard.hook(next)
    keyboard.hook(content)
    keyboard.wait()
