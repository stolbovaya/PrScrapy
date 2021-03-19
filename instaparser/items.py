# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItemPosts(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    user_id = scrapy.Field()
    photo = scrapy.Field()
    likes = scrapy.Field()
    post = scrapy.Field()


class InstaparserItemUsers(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    username = scrapy.Field()
    url = scrapy.Field()
    full_name = scrapy.Field()

class InstaparserItemLinks(scrapy.Item):
    # Подписки ( выборка всех user_to по user_from) и
    # подписчики  ( выборка всех user_from по user_to)
    _id = scrapy.Field()
    user_to = scrapy.Field()
    user_from = scrapy.Field()




