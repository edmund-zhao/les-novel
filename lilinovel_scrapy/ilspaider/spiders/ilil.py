import scrapy
from ilspaider.items import IlspaiderItem, ChapterItem
from logging import getLogger, Logger
class IlilSpider(scrapy.Spider):
    name = 'ilil'
    allowed_domains = ['linovel.net']
    start_urls = ['https://www.linovel.net/cat/21.html?sort=hot&sign=-1&page=1']

    def parse(self, response):
        """
        解析分类的起始URL链接，提取每本书的名称、作者与详细信息和其目录链接
        :param response: URL返回值
        :return:
        """
        nodes = response.xpath('//div[@class="book-info"]')

        for num , node in enumerate(nodes):
            try:
                item = IlspaiderItem()
                bookUrl = response.urljoin(node.xpath('./a/@href').extract_first())
                name = node.xpath('./a/text()').extract_first().strip()
                item['isVolume'] = True
                item['bookUrl'] = bookUrl
                item['name'] = name
                item['bookId'] = bookUrl.split('/')[-1][:-5]

            except:
                # 加入重试模块
                errorTimes = response.meta.get('errorTimes')
                print(response.meta)
                if errorTimes is None:
                    errorTimes = 1
                else:
                    errorTimes += 1
                print('Page Retry Times : ',errorTimes)
                if errorTimes <= 10:
                    yield scrapy.Request(response.request.url, callback=self.parse,
                                         dont_filter=True,
                                         meta = {'errorTimes' : errorTimes})
                else:
                    print('Page Error!')

            yield scrapy.Request(bookUrl,
                                 callback=self.parse_book,
                                 meta = {'item' : item}
                                 )
        nextPage = response.xpath('//ul[@class="pagination"]/li[last()]/@class').extract_first()
        if nextPage != "disabled":
            nextUrl = response.urljoin(response.xpath('//ul[@class="pagination"]/li[last()]/a/@href').extract_first())
            print(nextUrl)
            yield scrapy.Request(nextUrl, callback=self.parse)


    def parse_book(self, response):
        """
        用于解析小说的详情页面
        :param response:
        :return:
        """
        item = response.meta['item']
        try:

            tags = response.xpath('//div[@class="book-cats clearfix"]/a/text()').extract()
            # 分片去除 更新于 这三个字
            lastUpdate = response.xpath('//div[@class="book-last-update"]/text()').extract_first()[3:]
            bookCover = response.xpath('//div[@class="book-cover"]/a/@href').extract_first()
            details = ''
            for i in response.xpath('//div[@class="about-text text-content-actual"]/text()').extract():
                details += i.strip() + '\n'
            item['tags'] = tags
            item['details'] = details
            item['lastUpdate'] = lastUpdate
            item['bookCover'] = bookCover
        except:
            # 加入重试模块
            errorTimes = response.meta.get('errorTimes')
            if errorTimes is None:
                errorTimes = 1
            else:
                errorTimes += 1
            print('Book {} Retry Times : '.format(response.request.url.split('/')[-1][:-5]), errorTimes)
            if errorTimes <= 10:
                yield scrapy.Request(response.request.url, callback=self.parse_book,
                                     dont_filter=True,
                                     meta={'errorTimes': errorTimes,
                                           'item' : item})
            else:
                print('Book {}  Error!'.format(response.request.url.split('/')[-1][:-5]))



        # 对分卷于不分卷进行不同的处理
        if item['isVolume']:
            item['volume'] = []
            volumes = response.xpath('//div[@class="volume-info"]')
            for num, volume in enumerate(volumes):

                # 将Temp数据存入item['volume']中
                temp = {}

                volumeCover = volume.xpath('//div[@class="volume-cover"]/a/@href').extract_first()
                volumeTitle = volume.xpath('//div[@class="volume-title"]/a/text').extract_first()
                volumeChapter = volume.xpath('//div[@class="chapter"]/a')

                temp['volumeCover'] = volumeCover
                temp['volumeTitle'] = volumeTitle
                temp['sort'] = num
                temp['chapters'] = []

                for numc, chapter in enumerate(volumeChapter):

                    chapterUrl = response.urljoin(chapter.xpath('./@href').extract_first())
                    chapterId = chapterUrl.split('/')[-1][:-5]
                    chapterTitle = chapter.xpath('./text()').extract_first().strip()
                    temp['chapters'].append({
                        'chapterUrl': chapterUrl,
                        'chapterId': chapterId,
                        'chapterTitle' : chapterTitle,
                        'sort' : numc
                    })
                    yield scrapy.Request(chapterUrl,
                                         callback = self.parse_chapter,
                                         meta = {'item' : item}
                                         )
                item['volume'].append(temp)
            yield item

        else:
            pass


    def parse_chapter(self, response):
        """
        用于解析小说的内容
        :param response:
        :return:
        """
        chapterItem = ChapterItem()
        try:
            text = ""
            for i in response.xpath('//div[@class="article-text"]/p/text()'):
                if i == '\t':
                    continue
                text += i.extract() + "\n"
            chapterItem['content'] = text
            title = response.xpath('//div[@class="article-title"]/text()').extract_first().strip()
            update_time = response.xpath('//i[@class="icon-time"]/parent::div/text()[2]').extract_first().split('：')[-1]
            chapterItem['title'] = title
            chapterItem['updateTime'] = update_time
            chapterItem['ChapterId'] = response.url.split('/')[-1][:-5]
        except:
            # 加入重试模块
            errorTimes = response.meta.get('errorTimes')
            if errorTimes is None:
                errorTimes = 1
            else:
                errorTimes += 1
            print('Chapter {} Retry Times: '.format(response.request.url.split('/')[-1][:-5]), errorTimes)
            if errorTimes <= 10:
                yield scrapy.Request(response.request.url, callback=self.parse_chapter,
                                     dont_filter=True,
                                     meta={'errorTimes': errorTimes})
            else:
                print('Chapter {}  Error!'.format(response.request.url.split('/')[-1][:-5]))
        yield chapterItem

