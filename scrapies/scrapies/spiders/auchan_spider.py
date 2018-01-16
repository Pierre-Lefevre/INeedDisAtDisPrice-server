# -*- coding: utf-8 -*-
import scrapy

import glob
import re
import scrapies.utils as u
from scrapy.http import Request
from scrapies.items import Product


class AuchanSpider(scrapy.Spider):
    name = "auchan"
    allowed_domains = ["auchan.fr"]
    base_url = "https://www.auchan.fr"
    start_urls = [
        base_url + '/informatique/ordinateur-portable/c-7638110'
    ]

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
                if len(glob.glob("data/" + self.name + "/json/" + open_ssl_hash + '.json')) != 1 or len(glob.glob("data/" + self.name + "/img/" + open_ssl_hash + '.jpg')) != 1:
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
            x_price = response.xpath('//div[' + u.x_class('pricesBlock') + ']')

            price_old = x_price.xpath('.//del[' + u.x_class('product-price--oldPrice') + ']/text()').extract_first()
            if price_old is not None:
                price_old = u.string_to_float(re.sub(' [^ ]*$', '', price_old.strip()).replace(" ", "").replace(" ", ""))

            price = x_price.xpath('.//meta[@itemprop="price"]/@content').extract_first()
            if price is not None:
                price = u.string_to_float(price.strip())

            currency = x_price.xpath('.//meta[@itemprop="priceCurrency"]/@content').extract_first()
            if currency is not None:
                currency = currency.strip()


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


            yield item
