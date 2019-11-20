import requests
import json
import time
import hashlib
import keyboard
import queue
from objects import News

# 数据源url
start_url = 'https://www.toutiao.com/api/pc/feed/?category=news_hot&utm_source=toutiao&widen=1&max_behot_time={}&max_behot_time_tmp={}&tadrequire=true&as={}&cp={}'
url = 'https://www.toutiao.com'

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
}
cookies = {'tt_webid': '6649949084894053895'}  # cookies可从浏览器中查找，为了避免被头条禁止爬虫

# 已爬取的新闻队列
news_queue = queue.Queue(100);

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


def get_data(url, headers, cookies):
    """获取网页数据"""
    try:
        r = requests.get(url, headers=headers, cookies=cookies)
        return json.loads(r.text)
    except:
        raise "get data from toutiao failed"


def main(max_behot_time):
    # 获取as和cp参数值
    ascp = get_as_cp()
    # 格式化url
    data_url = start_url.format(max_behot_time, max_behot_time, ascp['as'], ascp['cp'])
    # 获取数据
    http_result = get_data(data_url, headers, cookies)
    data = http_result['data']
    for data_index in range(len(data)):
        item = data[data_index]
        title = item['title']
        source = item['source']
        source_url = item['source_url']
        if 'https' not in source_url:
            source_url = url + source_url
        news = News(title, source, source_url)
        news_queue.put(news)
    # 获取下一个链接的max_behot_time参数的值
    max_behot_time = str(http_result['next']['max_behot_time'])


if __name__ == '__main__':
    max_behot_time = '0'  # 初始为0，从初始数据中得到下一链接的此参数值
    print("欢迎来到今日头条命令行版，按page_down开始摸鱼")
    while True:
        try:
            if keyboard.is_pressed('esc'):
                print("好的伙计，我们努力工作")
                exit()
            elif keyboard.is_pressed('page_down'):
                if(news_queue.empty()):
                    main(max_behot_time)
                news_queue.get().print();
            else:
                pass
        except:
            break
