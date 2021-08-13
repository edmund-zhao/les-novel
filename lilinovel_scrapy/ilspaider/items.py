# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IlspaiderItem(scrapy.Item):
    # define the fields for your item here like:
    bookUrl = scrapy.Field()
    bookCover = scrapy.Field()
    bookId = scrapy.Field()
    name = scrapy.Field()
    author = scrapy.Field()
    details = scrapy.Field()
    tags = scrapy.Field()
    lastUpdate = scrapy.Field()
    isVolume = scrapy.Field()
    volume = scrapy.Field()
    pass

class ChapterItem(scrapy.Item):

    title = scrapy.Field()
    updateTime = scrapy.Field()
    ChapterId = scrapy.Field()
    content = scrapy.Field()
