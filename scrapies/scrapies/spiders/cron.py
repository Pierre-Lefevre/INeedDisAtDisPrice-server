# -*- coding: utf-8 -*-
import scrapy

import time
import tldextract
import scrapies.prices as p
from pymongo import MongoClient


class CronSpider(scrapy.Spider):
    name = "cron"
    start_urls = []
    prices_function = {}

    def __init__(self):
        self.prices_function = {
            "auchan": p.get_auchan_prices,
            "boulanger": p.get_boulanger_prices,
            "cdiscount": p.get_cdiscount_prices,
            "darty": p.get_darty_prices,
            "fnac": p.get_fnac_prices,
            "ldlc": p.get_ldlc_prices,
            "materiel": p.get_materiel_net_prices,
            "rueducommerce": p.get_rue_du_commerce_prices,
        }
        self.db = MongoClient()
        self.urls = self.db.iNeedDisAtDisPrice.products.find({}, {"_id": 0, "url": 1})
        self.start_urls = []
        for url in self.urls:
            self.start_urls.append(url["url"])

    def parse(self, response):
        url_extract = tldextract.extract(response.url)
        price, price_old, currency = self.prices_function[url_extract.domain](response)
        self.db.iNeedDisAtDisPrice.products.update(
            {"url": response.url},
            {"$push": {'price_history': {'date': time.strftime("%Y/%m/%d"), 'price_old': price_old, 'price': price, 'currency': currency}}}
        )
