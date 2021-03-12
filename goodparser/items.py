# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GoodparserItem(scrapy.Item):


    name = scrapy.Field()
    href = scrapy.Field()
    pictures = scrapy.Field()
    description = scrapy.Field()
    properties = scrapy.Field()
    properties_value = scrapy.Field()

    price = scrapy.Field()
    price_currency = scrapy.Field()
    price_unit = scrapy.Field()
    price_second = scrapy.Field()
    price_second_fract = scrapy.Field()
    price_second_currency = scrapy.Field()
    price_second_unit = scrapy.Field()

    _id = scrapy.Field()