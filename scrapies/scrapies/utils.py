# -*- coding: utf-8 -*-
import hashlib
import sys

CURRENCY_MAPPING = {
    '€': 'EUR',
    # '$': 'USD',
    # '£': 'GBP',
}

def get_platform():
    platforms = {
        'linux1' : 'Linux',
        'linux2' : 'Linux',
        'darwin' : 'OS X',
        'win32' : 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform
    return platforms[sys.platform]

def generate_open_ssl_hash(name):
    hash_object = hashlib.new('DSA')
    hash_object.update(name.encode('utf-8'))
    return hash_object.hexdigest()


def get_currency_code(currency_symbol):
    if get_platform() == "Linux":
        currency_symbol = currency_symbol.encode('utf-8')
    return CURRENCY_MAPPING[currency_symbol.strip()]


def string_to_float(string):
    return float(string.replace(",", "."))


def x_class(string):
    return 'contains(concat(" ", normalize-space(@class), " "), " ' + string + ' ")'
