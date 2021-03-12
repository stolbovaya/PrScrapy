# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface


import scrapy
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline


class GoodPicturesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['pictures']:
            for img in item['pictures']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def file_path(self, request, response=None, info=None, *, item=None):

        for el in info.downloading:
            file_name = el

        adapter = ItemAdapter(item)
        path = adapter.get('_id')
        if path:
            _file_path = f'leroymerlin/{path}/{file_name}.jpg'
        else:
            _file_path = f'leroymerlin/{file_name}.jpg'
        return _file_path

    def item_completed(self, results, item, info):
        if results:
            item['pictures'] = [itm[1] for itm in results if itm[0]]
        return item


class GoodDatabasePipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.goods

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        try:
            collection.insert_one(item)
        except Exception as e:
            print(e)
        return item


class GoodParsePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('description'):
            adapter['description'] = ' '.join(
                [el.strip().replace('\n', '').replace('\t', '').replace('\n', '') for el in adapter.get('description')
                 if el.strip()])

        try:
            if adapter.get('price'):
                adapter['price'] = int(adapter.get('price').replace(' ', ''))

        except ValueError:
            pass
        try:
            if adapter.get('price_second_fract'):
                adapter['price_second_fract'] = int(adapter.get('price_second_fract').replace(' ', ''))
            else:
                adapter['price_second_fract'] = 0

            if adapter.get('price_second'):
                adapter['price_second'] = int(adapter.get('price_second').replace(' ', '')) + adapter.get(
                    'price_second_fract') / 100
            else:
                adapter['price_second'] = 0 + adapter.get('price_second_fract') / 100
            adapter['price_second_fract'] = None
        except ValueError:
            pass

        try:
            if adapter.get('properties'):
                adapter['properties'] = dict(zip(adapter.get('properties'), [el.strip().replace('\n', '').replace('\t', '')
                                                                             for el in adapter.get('properties_value')]))
            adapter['properties_value'] = None
        except ValueError:
            pass
        return item
