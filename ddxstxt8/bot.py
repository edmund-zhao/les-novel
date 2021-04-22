import grequests
from lxml import etree

import getChapter
from getChapter import illegalStrip
import downloadAsEpub

class Bot():
    def __init__(self,bookUrl):
        self.site = "https://www.ddxstxt8.com/"
        self.bookId = "github/EdmundZhao"
        self.startUrl = bookUrl
    def run(self):
        epubList = []
        bookData = getChapter.get(self.startUrl)
        if bookData[0] == -1:
            return -1
        for respond in grequests.map(bookData[0]):
            respond.encoding = 'gbk'
            tree = etree.HTML(respond.text)
            h1 = tree.xpath('//div[@class="bookname"]/h1')[0].text
            contents = tree.xpath('//*[@id="content"]/text()')
            epubCode = '<h1>{}</h1>'.format(h1)
            print(h1)
            for i in contents:
                if '请记住本书首发域名' in i or '书友大本营' in i:
                    continue
                epubCode += "<p>" + i.strip() + "</p>"
            epubList.append(epubCode)
        downloadAsEpub.creat2epub(self.bookId,authorName=bookData[-1],
                                  chapterimgList=[],
                                  coverImgUrl=bookData[1],
                                  bookName=bookData[2],
                                  epubList=epubList)

Test = Bot('https://www.ddxstxt8.com/0_736/')
Test.run()
