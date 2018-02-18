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


class RueDuCommerceSpider(scrapy.Spider):
    name = "rue_du_commerce"
    allowed_domains = ["rueducommerce.fr"]
    base_url = "https://www.rueducommerce.fr"
    start_urls = [
        base_url + '/rayon/ordinateurs-64/ordinateur-portable-657'
        # base_url + '/rayon/ordinateurs-64/ordinateur-de-bureau-658',
        # base_url + '/rayon/ordinateurs-64/tablette-et-ipad-659',
        # base_url + '/rayon/composants-16/disque-dur-interne-238',
        # base_url + '/rayon/composants-16/disque-dur-externe-236',
        # base_url + '/rayon/composants-16/ssd-248',
        # base_url + '/rayon/composants-16/memoire-pc-245'
    ]
    already_crawled = u.get_already_crawled()
    nb_crawled = 0

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        u.update_already_crawled(self.already_crawled)

    def parse(self, response):

        # Yield list pages.
        x_pagination = response.xpath('//div[' + u.x_class('results-header') + ']')
        if x_pagination:
            url_next_page = x_pagination.xpath('.//a[' + u.x_class('next') + ']/@href').extract_first()
            if url_next_page is not None:
                yield Request(self.base_url + url_next_page.strip(), callback=self.parse)

        # Yield product pages.
        x_list = response.xpath('//div[' + u.x_class('products list') + ']')
        if x_list:
            urls = response.xpath('.//article/a/@href').extract()
            for url in urls:
                url = self.base_url + url.strip()
                open_ssl_hash = u.generate_open_ssl_hash(url)
                if open_ssl_hash not in self.already_crawled:
                    self.already_crawled.append(open_ssl_hash)
                    yield Request(url, callback=self.parse)

        # Yield product.
        x_product = response.xpath('//div[' + u.x_class('productsheet') + ']')
        if x_product and self.nb_crawled < 20 :
            self.nb_crawled += 1
            item = Product()

            # Categories
            x_categories = response.xpath('//ol[' + u.x_class('breadcrumb-chevron') + ']')

            main_category = x_categories.xpath('./li[1]//span/text()').extract_first()
            if main_category is not None:
                main_category = main_category.strip()

            categories = x_categories.xpath('./li[position() >= 2 and position() < last()]//span/text()').extract()
            if categories:
                for i, category in enumerate(categories):
                    categories[i] = category.strip()

            # Brand
            x_brand_name = response.xpath('//div[' + u.x_class('productDetails') + ']/h1')

            brand = x_brand_name.xpath('./span[' + u.x_class('brand') + ']//span/text()').extract_first()
            if brand is not None:
                brand = brand.strip()

            # Name
            name = re.sub(' +', ' ', ''.join(x_brand_name.xpath('.//text()').extract()).replace('\n', '').replace('\r', '').strip())

            # Price
            price, price_old, currency = p.get_rue_du_commerce_prices(response)

            # Image
            src = response.xpath('//div[' + u.x_class('verticalGallery') + ']//li[1]/a/@data-zoom-image').extract_first()
            if src is None:
                src = response.xpath('//div[' + u.x_class('verticalGallery') + ']//li[1]/a/@data-image').extract_first()
            if src is not None:
                src = src.strip()

            # Avis
            x_avis = response.xpath('//div[' + u.x_class('productDetails') + ']/div[' + u.x_class('productRating') + ']')

            rate = x_avis.xpath('.//span[' + u.x_class('icon-rating-stars') + ']/@content').extract_first()
            if rate is not None:
                rate = u.string_to_float(rate.strip())

            nb_avis = x_avis.xpath('.//span[@itemprop="reviewCount"]/text()').extract_first()
            if nb_avis is not None:
                nb_avis = int(re.sub('\D', ' ', nb_avis.strip()))

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
