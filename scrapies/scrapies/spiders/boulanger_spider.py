# -*- coding: utf-8 -*-
import scrapy

import glob
import re
import time
import scrapies.utils as u
from scrapy.http import Request
from scrapies.items import Product


class BoulangerSpider(scrapy.Spider):
    name = "boulanger"
    allowed_domains = ["boulanger.com"]
    base_url = "https://www.boulanger.com"
    start_urls = [
        base_url + '/c/tous-les-ordinateurs-portables'
    ]

    def parse(self, response):

        # Yield list pages.
        x_pagination = response.xpath('//div[' + u.x_class('navigationListe') + ']')
        if x_pagination:
            url_next_page = x_pagination.xpath('.//span[' + u.x_class('navPage navPage-right') + ']/a/@href').extract_first()
            if url_next_page is not None:
                yield Request(self.base_url + url_next_page.strip(), callback=self.parse)


        # Yield product pages.
        x_list = response.xpath('//div[' + u.x_class('productListe') + ']')
        if x_list:
            urls = x_list.xpath('.//div[' + u.x_class('designations') + ']/h2/a/@href').extract()
            for url in urls:
                url = self.base_url + url.strip()
                open_ssl_hash = u.generate_open_ssl_hash(url)
                if len(glob.glob("data/" + self.name + "/json/" + open_ssl_hash + '.json')) != 1 or len(glob.glob("data/" + self.name + "/img/" + open_ssl_hash + '.jpg')) != 1:
                    yield Request(url, callback=self.parse)


        # Yield product.
        x_product = response.xpath('//h1[@itemprop="name"]')
        if x_product:
            item = Product()


            # Categories
            x_categories = response.xpath('//div[@id="filAriane"]')

            main_category = x_categories.xpath('.//li[2]//a/text()').extract_first()
            if main_category is not None:
                main_category = main_category.strip()

            categories = x_categories.xpath('.//li[position() >= 3 and position() <= last()]//a/text()').extract()
            if categories:
                for i, category in enumerate(categories):
                    categories[i] = category.strip()


            # Name
            name = re.sub(' +', ' ', ''.join(x_product.xpath('./text()').extract()).replace('\n', '').replace('\r', '').strip())


            # Price
            x_info = response.xpath('//div[' + u.x_class('informations') + ']')
            x_price = x_info.xpath('.//div[' + u.x_class('price') + ']')

            price_old = x_price.xpath('./span[' + u.x_class('productStrikeoutPrice on') + ']//span[' + u.x_class('exponent') + ']/text()').extract_first()
            price_cent_old = x_price.xpath('./span[' + u.x_class('productStrikeoutPrice on') + ']//sup/span[' + u.x_class('fraction') + ']/text()').extract_first()
            if price_old is not None:
                if price_cent_old is not None:
                    price_old = u.string_to_float((price_old.strip() + "," + price_cent_old.strip()).replace(" ", ""))
                else:
                    price_old = u.string_to_float(price_old.strip().replace(" ", ""))

            price = x_price.xpath('./p/span[' + u.x_class('exponent') + ']/text()').extract_first()
            price_cent = x_price.xpath('./p/sup/span[' + u.x_class('fraction') + ']/text()').extract_first()
            if price is not None:
                if price_cent is not None:
                    price = u.string_to_float((price.strip() + "," + price_cent.strip()).replace(" ", ""))
                else:
                    price = u.string_to_float(price.strip().replace(" ", ""))

            currency = x_price.xpath('./p/sup/text()').extract_first()
            if currency is not None:
                currency = u.get_currency_code(currency.strip())


            # Image
            src = response.xpath('//span[@itemprop="gtin13"]/text()').extract_first().strip()
            if src is not None:
                src = "https://boulanger.scene7.com/is/image/Boulanger/" + src + "_h_f_l_0"


            # Avis
            x_avis = response.xpath('//div[' + u.x_class('top') + ']/div[' + u.x_class('right') + ']//span[' + u.x_class('rating') + ']')

            rate = x_avis.xpath('./@class').extract_first()
            if rate is not None:
                rate = re.sub('\D', '', rate.strip())
                if rate != "0":
                    if len(rate) > 1:
                        rate = rate[:1] + "," + rate[1:]
                    rate = u.string_to_float(rate)
                else:
                    rate = None

            nb_avis = x_avis.xpath('./span[' + u.x_class('link') + ']/text()').extract_first()
            if nb_avis is not None:
                nb_avis = int(re.sub('\D', '', nb_avis.strip()))


            item['store'] = self.name
            item['url'] = response.url
            item['main_category'] = main_category
            item['categories'] = categories
            item['brand'] = None
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
