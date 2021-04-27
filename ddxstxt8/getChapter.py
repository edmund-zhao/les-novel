import grequests
from lxml import etree

import re
headers = {
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
}
def get(bookUrl, session):
    chapterUrl = []
    try :
        respond = session.get(bookUrl, headers=headers, timeout=7)
        respond.encoding = 'gbk'
        tree = etree.HTML(respond.text)
        bookName = tree.xpath('//*[@id="info"]/h1')[0].text
        authorName = tree.xpath('//*[@id="info"]/p[1]')[0].text.split('：')[-1]
        coverUrl = 'https://www.ddxstxt8.com' + tree.xpath('//div[@id="fmimg"]/img')[0].get('src')
        bookName = illegalStrip(bookName).strip()
        authorName = illegalStrip(authorName).strip()
    except:
        print('网络错误')
        return -1, -1 , -1 ,-1
    for i in tree.xpath('//*[@id="list"]/dl/dd[*]/a/@href'):
        url = respond.url + i
        chapterUrl.append(grequests.get(url, session = session, headers = headers, timeout = 7))
    return chapterUrl , coverUrl, bookName, authorName

def illegalStrip(path):
    """
    :param path: 需要清洗的文件夹名字
    :return: 清洗掉Windows系统非法文件夹名字的字符串
    """
    path = re.sub(r'[？?\*|“《》<>:/]', '', str(path))
    return path
