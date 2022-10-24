# coding:utf-8
import requests
import re
import time
from bs4 import BeautifulSoup
import random
from pymongo import MongoClient
headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
}
cookies = {'__jsluid': '01625427b147ef66aa4abe848e4d0008'}
mongo = MongoClient(host='192.168.1.177')
db = mongo.fuzz
vul = db.vulnerability
count = 0


def get_urls():
    url = "http://ics.cnvd.org.cn/?title=&max=10000&offset=10"
    r = requests.get(url, headers=headers, cookies=cookies)
    html = r.text
    soup = BeautifulSoup(html, 'lxml')
    hrefs = []
    for tag in soup.find('tbody', id='tr').find_all('a', href=re.compile('http://www.cnvd.org.cn/flaw/show')):
        hrefs.append(tag.attrs['href'])
    print("Number of url is: %d" % len(hrefs))
    return hrefs


def get_content(url):
    global count
    if count > 50:
        return
    print("%i [URL]%s" % (count, url))
    r = requests.get(url, headers=headers, cookies=cookies)
    html = r.text
    soup = BeautifulSoup(html, 'lxml')
    tbody = soup.find('tbody')
    if not tbody:
        print("this url didn't has table, [URL]%s" % url)
        time.sleep(random.random())
        get_content(url)
        return
    trs = tbody.find_all('tr')
    if not trs:
        print("this url didn't has trs")
        return

    item = dict()
    item['title'] = soup.find("h1").text.strip()
    if db.vulnerability.find({'title': item['title']}).count() != 0:
        print 'Already', item['title']
        count += 1
        return
    print(item['title'])
    tr_len = len(tbody.find_all('tr'))
    for i in range(tr_len-1):
        td0 = trs[i].find_all('td')[0].text.strip()
        item[td0] = trs[i].find_all('td')[1].text.strip()

    # 爬取评分
    show_div = soup.find(id='showDiv')
    child_div = show_div.find('div')
    item['score'] = split_unicode(child_div.string, '：')
    vul.insert(item)
    print(item)
    count += 1


def split_unicode(string, sep):
    for i in range(len(string)):
        if string[i] == sep.decode('utf-8'):
            return string[i+1:]


def import_vuls():
    """
    爬取主函数
    :return:
    """
    # db.drop_collection('vulnerability')
    urls = get_urls()
    for url in urls:
        get_content(url)


if __name__ == '__main__':
    # url = 'http://www.cnvd.org.cn/flaw/show/CNVD-2017-14601'
    # get_content(url)
    import_vuls()
