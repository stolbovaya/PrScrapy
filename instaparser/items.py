# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    user_id = scrapy.Field()
    photo = scrapy.Field()
    likes = scrapy.Field()
    post = scrapy.Field()


class InstaparserItemFollowers(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    user_to = scrapy.Field()
    username = scrapy.Field()
    url = scrapy.Field()
    full_name = scrapy.Field()


class InstaparserItemFollowing(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    user_from = scrapy.Field()
    username = scrapy.Field()
    url = scrapy.Field()
    full_name = scrapy.Field()
