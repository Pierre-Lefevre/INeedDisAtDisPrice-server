# -*- coding: utf-8 -*-
import hashlib

CURRENCY_MAPPING = {
    '€': 'EUR',
    '$': 'USD',
    '£': 'GBP',
}


def generate_open_ssl_hash(name):
    hash_object = hashlib.new('DSA')
    hash_object.update(name.encode('utf-8'))
    return hash_object.hexdigest()


def get_currency_code(currency_symbol):
    return CURRENCY_MAPPING[currency_symbol.strip().encode('utf-8')]


def string_to_float(string):
    return float(string.replace(",", "."))


def x_class(string):
    return 'contains(concat(" ", normalize-space(@class), " "), " ' + string + ' ")'
