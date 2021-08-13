# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from ilspaider.items import IlspaiderItem, ChapterItem

class IlspaiderPipeline:
    def process_item(self, item, spider):
        return item

from pymongo import MongoClient
import hashlib

"""操作数据库"""
class MongoDBPipeline(object):

    # 打开数据库
    def open_spider(self, spider):
        db_uri = spider.settings.get('MONGODB_URI', '')
        db_name = spider.settings.get('MONOGDB_DB_NAME', 'ilnovel')

        self.db_client = MongoClient(db_uri)
        self.db = self.db_client[db_name]

    # 关闭数据库
    def close_spider(self, spider):
        self.db_client.close()

    # 对数据进行处理
    def process_item(self, item, spider):
        if isinstance(item, ChapterItem):
            item = dict(item)
            _id = hashlib.md5(str(item).encode('utf-8')).hexdigest()
            item['_id'] = _id
            self.db.chapters.save(item)

        elif isinstance(item,IlspaiderItem):
            item = dict(item)
            _id = hashlib.md5(str(item).encode('utf-8')).hexdigest()
            item['_id'] = _id
            self.db.info.save(item)
        return item
