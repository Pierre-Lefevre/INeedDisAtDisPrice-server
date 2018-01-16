# -*- coding: utf-8 -*-
import scrapy

import glob
import re
import scrapies.utils as u
from scrapy.http import Request
from scrapies.items import Product


class RueDuCommerceSpider(scrapy.Spider):
    name = "rue_du_commerce"
    allowed_domains = ["rueducommerce.fr"]
    base_url = "https://www.rueducommerce.fr"
    start_urls = [
        base_url + '/rayon/ordinateurs-64/pc-portable-5875'
    ]

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
                if len(glob.glob("data/" + self.name + "/json/" + open_ssl_hash + '.json')) != 1 or len(glob.glob("data/" + self.name + "/img/" + open_ssl_hash + '.jpg')) != 1:
                    yield Request(url, callback=self.parse)


        # Yield product.
        x_product = response.xpath('//div[' + u.x_class('productsheet') + ']')
        if x_product:
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
            x_price = response.xpath('//div[' + u.x_class('productBuy') + ']')

            price_old = x_price.xpath('.//div[' + u.x_class('discount-prices') + ']//p[' + u.x_class('price') + ']/text()').extract_first()
            if price_old is not None:
                price_old = u.string_to_float(price_old[:-1].strip().replace(" ", "").replace(" ", ""))

            price = x_price.xpath('.//div[' + u.x_class('price main') + ']/p/text()').extract_first()
            price_cent = x_price.xpath('.//div[' + u.x_class('price main') + ']/p/sup/text()').extract_first()

            currency = None
            if price is not None:
                currency = u.get_currency_code(price_cent[:1])

            if price is not None:
                if price_cent is not None:
                    price = u.string_to_float((price.strip() + "," + price_cent[1:].strip()).replace(" ", "").replace(" ", ""))
                else:
                    price = u.string_to_float(price.strip().replace(" ", "").replace(" ", ""))


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


            yield item
