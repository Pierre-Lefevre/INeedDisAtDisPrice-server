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


class LdlcSpider(scrapy.Spider):
    name = "ldlc"
    allowed_domains = ["ldlc.com"]
    base_url = "https://www.ldlc.com"
    # Only full list pages.
    start_urls = [
        base_url + '/informatique/ordinateur-portable/pc-portable/c4265/p1e0t7o0a1.html'
        # base_url + '/informatique/ordinateur-de-bureau/pc-de-marque/c4250/p1e0t7o0a1.html',
        # base_url + '/informatique/pieces-informatique/disque-dur-interne/c4697/p1e0t7o0a1.html',
        # base_url + '/informatique/pieces-informatique/disque-ssd/c4698/p1e0t7o0a1.html',
        # base_url + '/informatique/peripherique-pc/disque-dur-externe/c4652/p1e0t7o0a1.html',
        # base_url + '/informatique/pieces-informatique/memoire-pc/c4703/p1e0t7o0a1.html'
    ]
    already_crawled = u.get_already_crawled()
    nb_crawled = 0

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        u.update_already_crawled(self.already_crawled)

    def parse(self, response):

        # Yield product pages.
        x_list = response.xpath('//div[' + u.x_class('productListing') + ']')
        if x_list:
            urls = x_list.xpath('.//a[' + u.x_class('nom') + ']/@href').extract()
            for url in urls:
                url = url.strip()
                open_ssl_hash = u.generate_open_ssl_hash(url)
                if open_ssl_hash not in self.already_crawled:
                    self.already_crawled.append(open_ssl_hash)
                    yield Request(url, callback=self.parse)

        # Yield product.
        x_product = response.xpath('//div[' + u.x_class('product') + ']')
        if x_product and self.nb_crawled < 20 :
            self.nb_crawled += 1
            item = Product()

            # Categories
            x_categories = response.xpath('//ul[' + u.x_class('cheminDeFer') + ']')

            main_category = x_categories.xpath('./li[2]/div/a/span/text()').extract_first()
            if main_category is not None:
                main_category = main_category.strip()

            categories = x_categories.xpath('./li[position() >= 3 and position() <= last()]/div/a/span/text()').extract()
            if categories:
                for i, category in enumerate(categories):
                    categories[i] = category.strip()

            # Brand
            brand = response.xpath('//table[@id="productParametersList"]//div[text()="Marque"]/following::div[1]/a/text()').extract_first()
            if brand is not None:
                brand = brand.strip()

            # Name
            name = re.sub(' +', ' ', response.xpath('//h1/span[' + u.x_class('fn designation_courte') + ']/text()').extract_first().strip())

            # Price
            price, price_old, currency = p.get_ldlc_prices(response)

            # Image
            src = response.xpath('//img[@id="ctl00_cphMainContent_ImgProduct"]/@src').extract_first()
            if src is not None:
                src = src.strip()

            # Avis
            x_avis = response.xpath('//div[@id="productinfos"]//span[' + u.x_class('rating') + ']')

            rate = x_avis.xpath('./span[' + u.x_class('average') + ']/text()').extract_first()
            if rate is not None:
                rate = u.string_to_float(rate.strip())

            nb_avis = x_avis.xpath('./span[' + u.x_class('votes') + ']/text()').extract_first()
            if nb_avis is not None:
                nb_avis = int(nb_avis.strip())

            max_rate = x_avis.xpath('./span[' + u.x_class('best') + ']/text()').extract_first()
            if max_rate is not None:
                max_rate = int(max_rate.strip())

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
            item["max_rate"] = max_rate
            item["nb_avis"] = nb_avis
            item["price_history"] = [{'date': time.strftime("%Y/%m/%d"), 'price_old': price_old, 'price': price, 'currency': currency}]

            yield item
