# -*- coding: utf-8 -*-
import re
import scrapies.utils as u


def get_auchan_prices(response):
    x_price = response.xpath('//div[' + u.x_class('pricesBlock') + ']')

    price_old = x_price.xpath('.//del[' + u.x_class('product-price--oldPrice') + ']/text()').extract_first()
    if price_old is not None:
        price_old = u.string_to_float(re.sub(' [^ ]*$', '', price_old.encode('utf-8').strip()).replace(" ", "").replace(" ", ""))

    price = x_price.xpath('.//meta[@itemprop="price"]/@content').extract_first()
    if price is not None:
        price = u.string_to_float(price.encode('utf-8').strip().replace(" ", ""))

    currency = x_price.xpath('.//meta[@itemprop="priceCurrency"]/@content').extract_first()
    if currency is not None:
        currency = currency.strip()

    return price, price_old, currency


def get_boulanger_prices(response):
    x_info = response.xpath('//div[' + u.x_class('informations') + ']')
    x_price = x_info.xpath('.//div[' + u.x_class('price') + ']')

    price_old = x_price.xpath('./span[' + u.x_class('productStrikeoutPrice on') + ']//span[' + u.x_class('exponent') + ']/text()').extract_first()
    price_cent_old = x_price.xpath('./span[' + u.x_class('productStrikeoutPrice on') + ']//sup/span[' + u.x_class('fraction') + ']/text()').extract_first()
    if price_old is not None:
        if price_cent_old is not None:
            price_old = u.string_to_float((price_old.encode('utf-8').strip() + "," + price_cent_old.encode('utf-8').strip()).replace(" ", ""))
        else:
            price_old = u.string_to_float(price_old.encode('utf-8').strip().replace(" ", ""))

    price = x_price.xpath('./p/span[' + u.x_class('exponent') + ']/text()').extract_first()
    price_cent = x_price.xpath('./p/sup/span[' + u.x_class('fraction') + ']/text()').extract_first()
    if price is not None:
        if price_cent is not None:
            price = u.string_to_float((price.encode('utf-8').strip() + "," + price_cent.encode('utf-8').strip()).replace(" ", ""))
        else:
            price = u.string_to_float(price.encode('utf-8').strip().replace(" ", ""))

    currency = x_price.xpath('./p/sup/text()').extract_first()
    if currency is not None:
        currency = u.get_currency_code(currency.strip())

    return price, price_old, currency


def get_cdiscount_prices(response):
    x_price = response.xpath('//div[@id="fpBlocPrice"]')

    price_old = x_price.xpath('.//span[' + u.x_class('fpStriked') + ']/text()').extract_first()
    if price_old is not None:
        price_old = u.string_to_float(re.sub(' .*$', '', price_old.encode('utf-8').strip()).replace(" ", ""))

    price = x_price.xpath('.//span[' + u.x_class('fpPrice price jsMainPrice jsProductPrice') + ']/@content').extract_first()
    if price is not None:
        price = u.string_to_float(price.encode('utf-8').strip().replace(" ", ""))

    currency = x_price.xpath('.//meta[@itemprop="priceCurrency"]/@content').extract_first()
    if price is not None:
        currency = currency.strip()

    return price, price_old, currency


def get_darty_prices(response):
    x_price = response.xpath('//div[' + u.x_class('product_infos') + ']')

    price_old = x_price.xpath('.//span[' + u.x_class('darty_prix_barre_cont') + ']/span[' + u.x_class('darty_prix_barre') + ']/text()').extract_first()
    price_old_cent = x_price.xpath('.//span[' + u.x_class('darty_prix_barre_cont') + ']/span[' + u.x_class('darty_cents darty_prix_barre') + ']/text()').extract_first()

    if price_old is not None:
        if price_old_cent is not None:
            price_old = u.string_to_float((re.sub('\D', ' ', price_old.encode('utf-8').strip()) + "," + re.sub('\D', ' ', price_old_cent.encode('utf-8').strip())).replace(" ", ""))
        else:
            price_old = u.string_to_float(re.sub('\D', ' ', price_old.encode('utf-8').strip()).replace(" ", ""))

    price = x_price.xpath('.//meta[@itemprop="price"]/@content').extract_first()
    if price is not None:
        price = u.string_to_float(price.encode('utf-8').strip())

    currency = x_price.xpath('.//meta[@itemprop="priceCurrency"]/@content').extract_first()
    if currency is not None:
        currency = currency.strip()

    return price, price_old, currency


def get_fnac_prices(response):
    x_price = response.xpath('//div[' + u.x_class('f-priceBox') + ']')
    x_price_old = x_price.xpath('.//span[' + u.x_class('f-priceBox-price f-priceBox-price--old') + ']')
    x_price_new = x_price.xpath('.//span[' + u.x_class('f-priceBox-price f-priceBox-price--reco') + ']')

    price_old = x_price_old.xpath('./text()').extract_first()
    price_cent_old = x_price_old.xpath('./sup/text()').extract_first()
    if price_old is not None:
        if price_cent_old is not None:
            price_old = u.string_to_float((price_old.encode('utf-8').strip() + "," + price_cent_old[1:].encode('utf-8').strip()).replace(" ", ""))
        else:
            price_old = u.string_to_float(price_old[:-1].encode('utf-8').strip().replace(" ", ""))

    price = x_price_new.xpath('./text()').extract_first()
    price_cent = x_price_new.xpath('./sup/text()').extract_first()

    currency = None
    if price_cent is not None:
        currency = u.get_currency_code(price_cent[:1].strip())
    elif price is not None:
        currency = u.get_currency_code(price[-1:].strip())

    if price is not None:
        if price_cent is not None:
            price = u.string_to_float((price.encode('utf-8').strip() + "," + price_cent[1:].encode('utf-8').strip()).replace(" ", ""))
        else:
            price = u.string_to_float(price[:-1].encode('utf-8').strip().replace(" ", ""))

    return price, price_old, currency


def get_ldlc_prices(response):
    x_price = response.xpath('//span[' + u.x_class('blocprix') + ']')

    price_old = x_price.xpath('.//span[' + u.x_class('refPrice') + ']/text()').extract_first()
    if price_old is not None:
        price_old = u.string_to_float(price_old[:-1].encode('utf-8').strip().replace(" ", ""))

    price = x_price.xpath('.//span[' + u.x_class('price') + ']/text()').extract_first()
    price_cent = x_price.xpath('.//span[' + u.x_class('price') + ']/sup/text()').extract_first()

    currency = None
    if price is not None:
        currency = u.get_currency_code(price[-1:].strip())

    if price is not None:
        if price_cent is not None:
            price = u.string_to_float((price[:-1].encode('utf-8').strip() + "," + price_cent.encode('utf-8').strip()).replace(" ", ""))
        else:
            price = u.string_to_float(price[:-1].encode('utf-8').strip().replace(" ", ""))

    return price, price_old, currency


def get_materiel_net_prices(response):
    x_price = response.xpath('//div[@id="ProdInfoPrice"]')

    price_old = x_price.xpath('./div[' + u.x_class('prixReference') + ']/text()').extract_first()
    if price_old is not None:
        price_old = u.string_to_float(re.sub(' \D*$', '', price_old.encode('utf-8').strip()).replace(" ", ""))

    price = x_price.xpath('./span[' + u.x_class('hidden') + ']/text()').extract_first()

    currency = None
    if price is not None:
        currency = u.get_currency_code(re.sub('^.*\d | [^ ]*$', '', price.strip()))

    if price is not None:
        price = u.string_to_float(re.sub(' \D*$', '', price.encode('utf-8').strip()).replace(" ", ""))

    return price, price_old, currency


def get_rue_du_commerce_prices(response):
    x_price = response.xpath('//div[' + u.x_class('productBuy') + ']')

    price_old = x_price.xpath('.//div[' + u.x_class('discount-prices') + ']//p[' + u.x_class('price') + ']/text()').extract_first()
    if price_old is not None:
        price_old = u.string_to_float(price_old[:-1].encode('utf-8').strip().replace(" ", ""))

    price = x_price.xpath('.//div[' + u.x_class('price main') + ']/p/text()').extract_first()
    price_cent = x_price.xpath('.//div[' + u.x_class('price main') + ']/p/sup/text()').extract_first()

    currency = None
    if price is not None:
        currency = u.get_currency_code(price_cent[:1].strip())

    if price is not None:
        if price_cent is not None:
            price = u.string_to_float((price.encode('utf-8').strip() + "," + price_cent[1:].encode('utf-8').strip()).replace(" ", ""))
        else:
            price = u.string_to_float(price.encode('utf-8').strip().replace(" ", ""))

    return price, price_old, currency
