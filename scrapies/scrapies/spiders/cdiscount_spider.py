# -*- coding: utf-8 -*-
import scrapy

import re
import time
import scrapies.utils as u
import scrapies.prices as p
from scrapy import signals
from scrapy.http import Request
from scrapies.items import Product
from scrapy.xlib.pydispatch import dispatcher


class CdiscountSpider(scrapy.Spider):
    name = "cdiscount"
    allowed_domains = ["cdiscount.com"]
    base_url = "https://www.cdiscount.com"
    start_urls = [
        base_url + '/informatique/ordinateurs-pc-portables/pc-portables/l-1070992.html',
        base_url + '/informatique/achat-pc-ordinateur/tous-les-pc-de-bureau/l-1070840.html',
        base_url + '/informatique/disques-durs/disque-dur-externe-ssd/l-1073610.html',
        base_url + '/informatique/disques-durs/disques-durs-externes/l-1073602.html',
        base_url + '/informatique/disques-durs/disque-dur/l-1073632.html',
        base_url + '/informatique/memoire-ram/l-10716.html'
    ]
    first = True
    already_crawled = u.get_already_crawled()

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        u.update_already_crawled(self.already_crawled)

    def parse(self, response):

        # Yield list pages.
        x_pagination = response.xpath('//ul[@id="PaginationForm_ul"]')
        if x_pagination and self.first:
            self.first = False
            nb_page = x_pagination.xpath('./li[last()]/a/text()').extract_first()
            if nb_page is not None:
                for x in range(1, int(nb_page.strip())):
                    yield Request(response.url[:-5] + "-" + str(x) + response.url[-5:], callback=self.parse)

        # Yield product pages.
        x_list = response.xpath('//ul[@id="lpBloc"]')
        if x_list:
            urls = x_list.xpath('.//div[' + u.x_class('prdtBILDetails') + ']/a/@href').extract()
            for url in urls:
                url = url.strip()
                open_ssl_hash = u.generate_open_ssl_hash(url)
                if open_ssl_hash not in self.already_crawled:
                    self.already_crawled.append(open_ssl_hash)
                    yield Request(url, callback=self.parse)

        # Yield product.
        x_product = response.xpath('//h1[@itemprop="name"]')
        if x_product:
            item = Product()

            # Categories
            x_categories = response.xpath('//div[@id="bc"]')

            main_category = x_categories.xpath('.//li[3]//span/text()').extract_first()
            if main_category is not None:
                main_category = main_category.strip()

            categories = x_categories.xpath('.//li[position() >= 4 and position() < last()]//span/text()').extract()
            if categories:
                for i, category in enumerate(categories):
                    categories[i] = category.strip()

            # Brand
            brand = response.xpath('//table[' + u.x_class('fpDescTb fpDescTbPub') + ']//span[@itemprop="brand"]//span[@itemprop="name"]/text()').extract_first()
            if brand is not None:
                brand = brand.strip()

            # Name
            name = re.sub(' +', ' ', x_product.xpath('./text()').extract_first().strip())

            # Price
            price, price_old, currency = p.get_cdiscount_prices(response)

            # Image
            src = response.xpath('//div[' + u.x_class('fpMainImg') + ']/a[@itemprop="image"]/@href').extract_first().strip()

            # Avis
            x_avis = response.xpath('//div[' + u.x_class('topMainRating') + ']')

            rate = x_avis.xpath('//span[@itemprop="ratingValue"]/text()').extract_first()
            if rate is not None:
                rate = u.string_to_float(rate.strip())

            nb_avis = x_avis.xpath('//span[@itemprop="ratingCount"]/text()').extract_first()
            if nb_avis is not None:
                nb_avis = int(nb_avis.strip())

            item['store'] = self.name
            item['url'] = response.url
            item['main_category'] = main_category
            item['categories'] = categories
            item['brand'] = brand
            item['openssl_hash'] = u.generate_open_ssl_hash(item['url'])
            item['name'] = name
            item['price_old'] = price_old
            item['price'] = price
            item['currency'] = currency
            item["image_urls"] = [src]
            item["image_name"] = item['openssl_hash']
            item["rate"] = rate
            item["max_rate"] = 5
            item["nb_avis"] = nb_avis
            item["price_history"] = [{'date': time.strftime("%Y/%m/%d"), 'price_old': price_old, 'price': price, 'currency': currency}]

            yield item
