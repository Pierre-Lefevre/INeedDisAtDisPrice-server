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


class MaterielNetSpider(scrapy.Spider):
    name = "materiel_net"
    allowed_domains = ["materiel.net"]
    base_url = "https://www.materiel.net"
    start_urls = [
        base_url + '/pc-portable/?p=1'
        # base_url + '/ordinateur/?p=1',
        # base_url + '/tablette-tactile/?p=1',
        # base_url + '/disque-ssd/?p=1',
        # base_url + '/disque-dur/?p=1',
        # base_url + '/disque-dur-externe/?p=1',
        # base_url + '/barrette-memoire-pour-pc/?p=1',
        # base_url + '/barrette-memoire-pour-pc-portable/?p=1'
    ]
    already_crawled = u.get_already_crawled()

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        u.update_already_crawled(self.already_crawled)

    def parse(self, response):

        # Yield list pages.
        x_pagination = response.xpath('//ul[' + u.x_class('pagination pagination-sm') + ']')
        if x_pagination:
            url_next_page = x_pagination.xpath('./li[position() = last()]/a/@href').extract_first()
            if url_next_page is None:
                url_next_page = x_pagination.xpath('./li[position() = (last() - 1)]/a/@href').extract_first()
            if url_next_page is not None:
                yield Request(self.base_url + url_next_page, callback=self.parse)

        # Yield product pages.
        x_list = response.xpath('//table[' + u.x_class('ProdList') + ']')
        if x_list:
            urls = x_list.xpath('.//td[' + u.x_class('Photo') + ']/span/@data-href').extract()
            for url in urls:
                url = self.base_url + url
                open_ssl_hash = u.generate_open_ssl_hash(url)
                if open_ssl_hash not in self.already_crawled:
                    self.already_crawled.append(open_ssl_hash)
                    yield Request(url, callback=self.parse)

        # Yield product.
        x_product = response.xpath('//div[@id="prod"]')
        if x_product:
            item = Product()

            # Categories
            x_categories = response.xpath('//nav[@id="breadcrumb"]')

            categories = x_categories.xpath('.//li[position() >= 3 and position() < last()]/a/text()').extract()
            if categories:
                for i, category in enumerate(categories):
                    categories[i] = category.strip()

            # Brand
            brand = x_categories.xpath('.//li[2]/a/text()').extract_first()
            if brand is not None:
                brand = brand.strip()

            # Name
            name = re.sub(' +', ' ', ''.join(response.xpath('//h1[@id="ProdTitle"]//text()').extract()).replace('\n', '').replace('\r', '').strip())

            # Price
            price, price_old, currency = p.get_materiel_net_prices(response)

            # Image
            src = response.xpath('//div[' + u.x_class('swiper-wrapper') + ']//a/@data-zoom-image').extract_first()
            if src is None:
                src = response.xpath('//div[@id="container-image"]/@data-zoom-image').extract_first()
            if src is not None:
                src = src.strip()

            # Avis
            x_avis = response.xpath('//div[' + u.x_class('headerAvisClients') + ']')

            rate = x_avis.xpath('.//span[' + u.x_class('noteUser') + ']/text()').extract_first()
            if rate is not None:
                rate = u.string_to_float(rate.strip())

            max_rate = x_avis.xpath('.//span[' + u.x_class('noteUser') + ']/following-sibling::span[1]/text()').extract_first()
            if max_rate is not None:
                max_rate = u.string_to_float(max_rate.strip())

            nb_avis = x_avis.xpath('.//span[@id="avisCount"]/span/text()').extract_first()
            if nb_avis is not None:
                nb_avis = int(nb_avis.strip())

            item['store'] = self.name
            item['url'] = response.url
            item['main_category'] = "Informatique"
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
            item["max_rate"] = max_rate
            item["nb_avis"] = nb_avis
            item["price_history"] = [{'date': time.strftime("%Y/%m/%d"), 'price_old': price_old, 'price': price, 'currency': currency}]

            yield item
