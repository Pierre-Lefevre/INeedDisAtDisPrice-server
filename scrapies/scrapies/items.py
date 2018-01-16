# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapiesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class Product(scrapy.Item):
    store = scrapy.Field()
    url = scrapy.Field()
    main_category = scrapy.Field()
    categories = scrapy.Field()
    brand = scrapy.Field()
    openssl_hash = scrapy.Field()
    name = scrapy.Field()
    price_old = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    image_urls = scrapy.Field()
    image_name = scrapy.Field()
    images = scrapy.Field()
    rate = scrapy.Field()
    max_rate = scrapy.Field()
    nb_avis = scrapy.Field()
    price_history = scrapy.Field()
