# -*- coding: utf-8 -*-
import scrapy

import glob
import re
import scrapies.utils as u
from scrapy.http import Request
from scrapies.items import Product


class DartySpider(scrapy.Spider):
    name = "darty"
    allowed_domains = ["darty.com"]
    base_url = "https://www.darty.com"
    start_urls = [
        base_url + '/nav/extra/list?p=200&s=topa&cat=26055'
    ]

    def parse(self, response):

        # Yield list pages.
        x_pagination = response.xpath('//body[@id="darty_liste_produit"]//div[@id="main_pagination_top"]/div[' + u.x_class('darty_product_list_pages_list') + ']')
        if x_pagination:
            url_next_page = x_pagination.xpath('./a[text()="\xa0Page suivante"][last()]/@href').extract_first()
            if url_next_page is not None:
                yield Request(self.base_url + url_next_page.strip(), callback=self.parse)


        # Yield product pages.
        x_list = response.xpath('//body[@id="darty_liste_produit"]//div[@id="main_products_list"]')
        if x_list:
            urls = x_list.xpath('.//div[' + u.x_class('infos_container') + ']/h2/a/@href').extract()
            for url in urls:
                url = self.base_url + url.strip()
                open_ssl_hash = u.generate_open_ssl_hash(url)
                if len(glob.glob("data/" + self.name + "/json/" + open_ssl_hash + '.json')) != 1 or len(glob.glob("data/" + self.name + "/img/" + open_ssl_hash + '.jpg')) != 1:
                    yield Request(url, callback=self.parse)


        # Yield product.
        x_product = response.xpath('//body[@id="page_product"]')
        if x_product:
            item = Product()


            # Categories
            x_categories = response.xpath('//ul[@id="dartyCom_fil_ariane"]')

            main_category = x_categories.xpath('./li[2]/a/text()').extract_first()
            if main_category is not None:
                main_category = main_category.strip()

            categories = x_categories.xpath('./li[position() >= 3 and position() < last()]/a/text()').extract()
            if categories:
                for i, category in enumerate(categories):
                    categories[i] = category.strip()


            # Brand
            brand = response.xpath('//a[@id="darty_product_brand"]/text()').extract_first()
            if brand is not None:
                brand = brand.strip()


            # Name
            name = re.sub(' +', ' ', ''.join(response.xpath('//h1[' + u.x_class('product_head') + ']//div[' + u.x_class('product_name') + ']/span//text()').extract()).replace('\n', '').replace('\r', '').strip())


            # Price
            x_price = response.xpath('//div[' + u.x_class('product_infos') + ']')

            price_old = x_price.xpath('.//span[' + u.x_class('darty_prix_barre_cont') + ']/span[' + u.x_class('darty_prix_barre') + ']/text()').extract_first()
            price_old_cent = x_price.xpath('.//span[' + u.x_class('darty_prix_barre_cont') + ']/span[' + u.x_class('darty_cents darty_prix_barre') + ']/text()').extract_first()

            if price_old is not None:
                if price_old_cent is not None:
                    price_old = u.string_to_float((re.sub('\D', ' ', price_old.strip()) + "," + re.sub('\D', ' ', price_old_cent.strip())).replace(" ", ""))
                else:
                    price_old = u.string_to_float(re.sub('\D', ' ', price_old.strip()).replace(" ", ""))

            price = x_price.xpath('.//meta[@itemprop="price"]/@content').extract_first()
            if price is not None:
                price = u.string_to_float(price.strip())

            currency = x_price.xpath('.//meta[@itemprop="priceCurrency"]/@content').extract_first()
            if currency is not None:
                currency = currency.strip()


            # Image
            src = response.xpath('//div[' + u.x_class('darty_product_picture_main_pic_container') + ']/div[1]//img/@src').extract_first()
            if src is not None:
                src = src.strip()


            # Avis
            x_avis = response.xpath('//div[' + u.x_class('bloc_reviews_resume') + ']')

            rate = x_avis.xpath('//meta[@itemprop="ratingValue"]/@content').extract_first()
            if rate is not None:
                rate = u.string_to_float(rate.strip())

            max_rate = x_avis.xpath('//div[' + u.x_class('bloc_reviews_note') + ']/sub/text()').extract_first()
            if max_rate is not None:
                max_rate = int(re.sub('\D', ' ', max_rate.strip()))

            nb_avis = x_avis.xpath('//meta[@itemprop="ratingCount"]/@content').extract_first()
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
            item["max_rate"] = max_rate
            item["nb_avis"] = nb_avis


            yield item
