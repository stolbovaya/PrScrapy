# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

# db.InstaparserItemLinks.createIndex( { user_to: 1, user_from: 1 }, { unique: true } )
class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instagram

    def process_item(self, item, spider):
        collection = self.mongo_base[item.__class__.__name__]
        try:
            collection.insert_one(item)
        except Exception as e:
            print(e)
        return item
