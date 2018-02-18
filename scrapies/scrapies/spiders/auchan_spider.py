# -*- coding: utf-8 -*-
import scrapy

import time
import scrapies.utils as u
import scrapies.prices as p
from scrapy import signals
from scrapy.http import Request
from scrapies.items import Product
from scrapy.xlib.pydispatch import dispatcher


class AuchanSpider(scrapy.Spider):
    name = "auchan"
    allowed_domains = ["auchan.fr"]
    base_url = "https://www.auchan.fr"
    start_urls = [
        base_url + '/informatique/ordinateur-portable/c-7638110'
        # base_url + '/informatique/ordinateur-de-bureau/c-7638112',
        # base_url + '/informatique/tablette-tactile/c-7328319',
        # base_url + '/informatique/stockage/disque-dur-interne/c-6721660',
        # base_url + '/informatique/stockage/disque-dur-externe/c-8216',
        # base_url + '/informatique/composant-assemblage/barrette-memoire/c-201612291119'
    ]
    already_crawled = u.get_already_crawled()

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        u.update_already_crawled(self.already_crawled)

    def parse(self, response):

        # Yield list pages.
        x_pagination = response.xpath('//nav[' + u.x_class('ui-pagination') + ']')
        if x_pagination:
            url_next_page = x_pagination.xpath('.//a[' + u.x_class('ui-pagination--next') + ']/@href').extract_first()
            if url_next_page is not None:
                yield Request(self.base_url + url_next_page.strip(), callback=self.parse)

        # Yield product pages.
        x_list = response.xpath('//div[' + u.x_class('product-list--container') + ']')
        if x_list:
            urls = x_list.xpath('.//div[' + u.x_class('product-item--wrapper') + ']/a/@href').extract()
            for url in urls:
                url = self.base_url + url.strip()
                open_ssl_hash = u.generate_open_ssl_hash(url)
                if open_ssl_hash not in self.already_crawled:
                    self.already_crawled.append(open_ssl_hash)
                    yield Request(url, callback=self.parse)

        # Yield product.
        x_product = response.xpath('//div[' + u.x_class('product-detail') + ']')
        if x_product:
            item = Product()

            # Categories
            x_categories = response.xpath('//div[' + u.x_class('ui-breadcrumb--scroller') + ']/nav')

            main_category = x_categories.xpath('./span[2]/meta[@itemprop="name"]/@content').extract_first()
            if main_category is not None:
                main_category = main_category.strip()

            categories = x_categories.xpath('./span[position() >= 3 and position() < last()]/meta[@itemprop="name"]/@content').extract()
            if categories:
                for i, category in enumerate(categories):
                    categories[i] = category.strip()

            # Brand
            x_brand_name = response.xpath('//div[' + u.x_class('product-detail--wrapper') + ']')

            brand = x_brand_name.xpath('./meta[@itemprop="brand"]/@content').extract_first()
            if brand is not None:
                brand = brand.strip()

            # Name
            name = x_brand_name.xpath('./h1[' + u.x_class('product-detail--title') + ']/text()').extract_first().replace('\n', '').replace('\r', '').strip()

            # Price
            price, price_old, currency = p.get_auchan_prices(response)

            # Image
            src = response.xpath('//div[' + u.x_class('x-scroller') + ']/label[1]//img/@src').extract_first()
            if src is not None:
                src = src.strip()

            # Avis
            x_avis = response.xpath('//div[' + u.x_class('product-detail--rating') + ']')

            rate = x_avis.xpath('.//meta[@itemprop="ratingValue"]/@content').extract_first()
            if rate is not None:
                rate = u.string_to_float(rate.strip())

            nb_avis = x_avis.xpath('.//meta[@itemprop="reviewCount"]/@content').extract_first()
            if nb_avis is not None:
                nb_avis = int(nb_avis.strip())

            max_rate = x_avis.xpath('.//span[' + u.x_class('ui-rating--background') + ']/i[' + u.x_class('icon-auchan-82') + ']').extract()
            max_rate = len(max_rate) if max_rate else None

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
