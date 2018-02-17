# -*- coding: utf-8 -*-
import os
import sys
import json
import hashlib

CURRENCY_MAPPING = {
    '€': 'EUR',
    '$': 'USD',
    '£': 'GBP',
}


def get_already_crawled():
    if get_platform() == "Windows":
        with open(os.path.join(os.path.dirname(__file__), '..', 'already_crawled.json'), 'r', encoding='utf-8') as inputfile:
            return json.load(inputfile)
    else:
        with open(os.path.join(os.path.dirname(__file__), '..', 'already_crawled.json'), 'r') as inputfile:
            return json.load(inputfile)


def update_already_crawled(data):
    if get_platform() == "Windows":
        with open(os.path.join(os.path.dirname(__file__), '..', 'already_crawled.json'), 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, ensure_ascii=False)
    else:
        with open(os.path.join(os.path.dirname(__file__), '..', 'already_crawled.json'), 'w') as outfile:
            json.dump(data, outfile, ensure_ascii=False)


def get_platform():
    platforms = {
        'linux1': 'Linux',
        'linux2': 'Linux',
        'darwin': 'OS X',
        'win32': 'Windows'
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
