import time
import ast
import re
import requests
import createEpub
from lxml import etree
bookId = "2778"
authorName = "小林湖底"
bookName = "家里蹲吸血姬的苦闷"
bookCoverUrl = "https://w.linovelib.com/files/article/image/2/2778/2778s.jpg"
epubList, chapterimgList = [], []
start_url = "https://w.linovelib.com/novel/2778/132660.html" #"https://w.linovelib.com/novel/2734/catalog"


host = "https://w.linovelib.com"
headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"}

s = requests.Session()
s.mount('http://', requests.adapters.HTTPAdapter(max_retries=5))
s.mount('https://', requests.adapters.HTTPAdapter(max_retries=5))
response = s.get(start_url, headers=headers, timeout=5)
tree = etree.HTML(response.text)

while True:
    chapterName = tree.xpath('//*[@id="atitle"]/text()')[0]
    is_next = tree.xpath('//*[@id="footlink"]/a[4]/text()')[0]
    epubCodes = '<h1>{}</h1>'.format(chapterName.strip())
    imgCode = ''
    for book in tree.xpath('//*[@id="acontent"]/p'):
        if book.text is not None:
            if len(book.text.strip()) == 0:
                continue
            epubCodes += '<p>{}</p>'.format(book.text.strip())
    numb = 0
    for img in tree.xpath('//*[@id="acontent"]/div[*]/img'):
        imgUrl = img.get('src')
        try:
            imgContent = s.get(imgUrl, headers=headers, timeout=10).content
        except:
            continue
        chapterimg = createEpub.epub.EpubItem(
            file_name="images/" + bookId + '_' + str(response.url.split('/')[-1][:-5]) + '_' + str(numb) + '.png',
            content=imgContent)
        chapterimgList.append(chapterimg)
        imgCode += '<p><img src=' + "images/" + bookId + '_' + str(response.url.split('/')[-1][:-5]) + '_' + str(
            numb) + '.png' + '></p>'
        numb += 1
    for img in tree.xpath('//*[@id="acontent"]/p[*]/img'):
        imgUrl = img.get('src')
        try:
            imgContent = s.get(imgUrl, headers=headers, timeout=10).content
        except:
            continue
        chapterimg = createEpub.epub.EpubItem(
            file_name="images/" + bookId + '_' + str(response.url.split('/')[-1][:-5]) + '_' + str(numb) + '.png',
            content=imgContent)
        chapterimgList.append(chapterimg)
        imgCode += '<p><img src=' + "images/" + bookId + '_' + str(response.url.split('/')[-1][:-5]) + '_' + str(
            numb) + '.png' + '></p>'
        numb += 1
    epubList.append(epubCodes + imgCode)
    if is_next == '下一页'  or is_next == '下一章':
        r = re.findall(r'<script type="text/javascript">var ReadParams=([\s\S]+?)</script>', response.text, re.M)
        url_next = re.findall(r"url_next:'([\s\S]+?)'",r[0], re.M)[0]
        time.sleep(0.6)
        response = s.get(host + url_next, headers=headers, timeout=5)
        tree = etree.HTML(response.text)
        print(response.url)

    else:
        createEpub.creat2epub(bookId,bookName,authorName,bookCoverUrl,chapterimgList,epubList)
        break
    time.sleep(0.6)

#soup = BeautifulSoup(driver.page_source,'html.parser')


