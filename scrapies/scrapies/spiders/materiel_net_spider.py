# -*- coding: utf-8 -*-
import scrapy

import glob
import re
import scrapies.utils as u
from scrapy.http import Request
from scrapies.items import Product


class MaterielNetSpider(scrapy.Spider):
    name = "materiel_net"
    allowed_domains = ["materiel.net"]
    base_url = "https://www.materiel.net"
    start_urls = [
        base_url + '/pc-portable/?p=1'
    ]

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
                if len(glob.glob("data/" + self.name + "/json/" + open_ssl_hash + '.json')) != 1 or len(glob.glob("data/" + self.name + "/img/" + open_ssl_hash + '.jpg')) != 1:
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
            x_price = response.xpath('//div[@id="ProdInfoPrice"]')

            price_old = x_price.xpath('./div[' + u.x_class('prixReference') + ']/text()').extract_first()
            if price_old is not None:
                price_old = u.string_to_float(re.sub(' \D*$', '', price_old.strip()).replace(" ", ""))

            price = x_price.xpath('./span[' + u.x_class('hidden') + ']/text()').extract_first()

            currency = None
            if price is not None:
                currency = u.get_currency_code(re.sub('^.*\d | [^ ]*$', '', price.strip()))

            if price is not None:
                price = u.string_to_float(re.sub(' \D*$', '', price.strip()).replace(" ", ""))


            # Image
            src = response.xpath('//div[' + u.x_class('swiper-wrapper') + ']//a/@data-zoom-image').extract_first()
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


            yield item
