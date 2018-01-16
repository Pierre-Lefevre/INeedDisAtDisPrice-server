# -*- coding: utf-8 -*-
import scrapy

import glob
import re
import scrapies.utils as u
from scrapy.http import Request
from shutil import copyfile
from scrapies.items import Product


class FnacSpider(scrapy.Spider):
    name = "fnac"
    allowed_domains = ["fnac.com"]
    base_url = "https://www.fnac.com"
    start_urls = [
        base_url + '/Tous-les-ordinateurs-portables/Ordinateurs-portables/nsh154425/w-4?PageIndex=1',
        base_url + '/Tous-les-PC-de-bureau/Ordinateur-de-bureau/nsh51426/w-4?PageIndex=1',
        base_url + '/Toutes-les-tablettes/Toutes-les-tablettes/nsh227099/w-4?PageIndex=1',
        base_url + '/Tous-les-disques-durs/Disque-Dur/nsh119663/w-4?PageIndex=1',
        base_url + '/SearchResult/ResultList.aspx?SCat=8!1%2c8136!2&Search=ramPageIndex=1',
    ]
    src_no_image = "https://www4-fr.fnac-static.com/Nav/Images/Noscan/noscan_340x340.gif"

    def parse(self, response):

        # Yield list pages.
        x_pagination = response.xpath('//ul[' + u.x_class('Pager bottom-toolbar') + ']')
        if x_pagination:
            url_next_page = x_pagination.xpath('.//a[' + u.x_class('prevnext actionNext') + ']/@href').extract_first()
            if url_next_page is not None:
                yield Request(url_next_page, callback=self.parse)


        # Yield product pages.
        x_list = response.xpath('//ul[' + u.x_class('articleList') + ']')
        if x_list:
            urls = x_list.xpath('.//p[' + u.x_class('Article-desc') + ']/a/@href').extract()
            for url in urls:
                open_ssl_hash = u.generate_open_ssl_hash(url)
                if len(glob.glob("data/" + self.name + "/json/" + open_ssl_hash + '.json')) != 1 or len(glob.glob("data/" + self.name + "/img/" + open_ssl_hash + '.jpg')) != 1:
                    yield Request(url, callback=self.parse)


        # Yield product.
        x_product = response.xpath('//div[' + u.x_class('f-productPage') + ']')
        if x_product:
            item = Product()


            # Categories
            x_categories = response.xpath('//ul[' + u.x_class('f-breadcrumb') + ']')

            main_category = x_categories.xpath('./li[2]/a/text()').extract_first()
            if main_category is not None:
                main_category = main_category.strip()

            categories = x_categories.xpath('./li[position() >= 3]/a/text()').extract()
            if categories:
                for i, category in enumerate(categories):
                    categories[i] = category.strip()


            # Name
            name = response.xpath('//h1[' + u.x_class('f-productHeader-Title') + ']/text()').extract_first().strip()


            # Price
            x_price = response.xpath('//div[' + u.x_class('f-priceBox') + ']')
            x_price_old = x_price.xpath('.//span[' + u.x_class('f-priceBox-price f-priceBox-price--old') + ']')
            x_price_new = x_price.xpath('.//span[' + u.x_class('f-priceBox-price f-priceBox-price--reco') + ']')

            price_old = x_price_old.xpath('./text()').extract_first()
            price_cent_old = x_price_old.xpath('./sup/text()').extract_first()
            if price_old is not None:
                if price_cent_old is not None:
                    price_old = u.string_to_float((price_old + "," + price_cent_old[1:].strip()).replace(" ", ""))
                else:
                    price_old = u.string_to_float(price_old[:-1].strip().replace(" ", ""))

            price = x_price_new.xpath('./text()').extract_first()
            price_cent = x_price_new.xpath('./sup/text()').extract_first()

            currency = None
            if price_cent is not None:
                currency = u.get_currency_code(price_cent[:1])
            elif price is not None:
                currency = u.get_currency_code(price[-1:])

            if price is not None:
                if price_cent is not None:
                    price = u.string_to_float((price + "," + price_cent[1:].strip()).replace(" ", ""))
                else:
                    price = u.string_to_float(price[:-1].strip().replace(" ", ""))


            # Image
            src = response.xpath('//img[' + u.x_class('f-productVisuals-mainMedia') + ']/@src').extract_first().strip()


            # Avis
            x_avis = response.xpath('//div[' + u.x_class('f-review-header') + ']')

            rate = x_avis.xpath('.//div[' + u.x_class('f-review-headerRate') + ']/text()').extract_first()
            if rate is not None:
                rate = u.string_to_float(rate.strip())

            max_rate = x_avis.xpath('.//span[' + u.x_class('f-review-headerRateTotal') + ']/text()').extract_first()
            if max_rate is not None:
                max_rate = u.string_to_float(max_rate.strip().replace("/", ""))

            nb_avis = response.xpath('//div[' + u.x_class('f-productHeader-review') + ']//span[' + u.x_class('f-productHeader-reviewLabel') + ']/text()').extract_first()
            if nb_avis is not None:
                nb_avis = u.string_to_float(re.sub("\D", "", nb_avis.strip()))


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
            item["max_rate"] = max_rate
            item["nb_avis"] = nb_avis


            if src == self.src_no_image:
                copyfile("data/default.jpg", "data/" + self.name + "/img/" + item["image_name"] + ".jpg")


            yield item
