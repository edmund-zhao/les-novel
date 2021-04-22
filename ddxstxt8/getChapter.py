import grequests
import requests
from lxml import etree
from requests.adapters import HTTPAdapter

headers = {
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
}
def get(bookUrl):
    chapterUrl = []
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=3))
    s.mount('https://', HTTPAdapter(max_retries=3))
    respond = s.get(bookUrl,headers = headers, timeout = 7)
    respond.encoding = 'gbk'
    tree = etree.HTML(respond.text)
    try :
        bookName = tree.xpath('//*[@id="info"]/h1')[0].text
        authorName = tree.xpath('//*[@id="info"]/p[1]')[0].text.split('：')[-1]
        coverUrl = 'https://www.ddxstxt8.com' + tree.xpath('//div[@id="fmimg"]/img')[0].get('src')
    except:
        print('网络错误')
        return -1, -1 , -1 ,-1
    for i in tree.xpath('//*[@id="list"]/dl/dd[*]/a/@href'):
        url = respond.url + i
        chapterUrl.append(grequests.get(url ,session = s, headers = headers))
    return chapterUrl , coverUrl, bookName, authorName
t = get('https://www.ddxstxt8.com/0_736/')

for respond in grequests.map(t[0],gtimeout=10):
    respond.encoding = 'gbk'
    tree = etree.HTML(respond.text)
    h1 = tree.xpath('//div[@class="bookname"]/h1')[0].text
    content = tree.xpath('//*[@id="content"]/text()[*]')
    print(h1)
    for i in content:
        print(i)
