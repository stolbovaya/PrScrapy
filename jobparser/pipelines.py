# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import copy

from itemadapter import ItemAdapter
from pymongo import MongoClient


def get_salary(list_salary):
    rez = {'max_salary': None, 'min_salary': None, 'currency': None}

# -------------------------Убираем пробелы, руб., пустые элементы-----------------
    list_salary = [x.strip(' ').replace(u'\xa0', '').replace('руб.', '') for x in list_salary if
                   x.strip(' ').replace(u'\xa0', '').replace('руб.', '')]

    if len(list_salary) > 0:
        rez['currency'] = 'RUB' # по умолчанию проставляем руб.
# обработка з.п. для SJ (для диапозона и точного значения з.п.). Для HH  значения rez всегда будут None-----------------
        try:
            rez['min_salary'] = int(list_salary[0])
            rez['max_salary'] = rez['min_salary']
        except ValueError:
            pass

        if len(list_salary) == 2 and rez['min_salary'] is not None:
            try:
                rez['max_salary'] = int(list_salary[1])
            except ValueError:
                pass
# конец обработки з.п. для sj-------------------------

# Обработка 'от', 'до' и валюты для SJ и HH
        if list_salary.count('USD') > 0:
            rez['currency'] = 'USD'
        if list_salary.count('USD') > 0:
            rez['currency'] = 'EUR'
        try:
            rez['min_salary'] = int(list_salary[list_salary.index('от') + 1])
        except ValueError:
            pass

        try:
            rez['max_salary'] = int(list_salary[list_salary.index('до') + 1])
        except ValueError:
            pass
    return rez


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancies_2021

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('salary'):
            # можно разбить на get_salary_HH и get_salary_SJ по значению поля spider.name
            adapter['salary'] = get_salary(adapter['salary'])
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item
