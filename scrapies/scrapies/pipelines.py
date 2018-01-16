# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = ""

    def process_item(self, item, spider):
        # self.file = open('data/' + spider.name + '/json/%s.json' % item["openssl_hash"], 'w', encoding='utf-8')
        self.file = open('data/' + spider.name + '/json/%s.json' % item["openssl_hash"], 'w')
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        # self.file.write(line)
        self.file.write(line.encode('utf-8'))
        return item

    def spider_closed(self, spider):
        self.file.close()


class ImagesCustomPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        return [Request(x, meta={'store': item["store"], 'image_name': item["image_name"]}) for x in item.get('image_urls', [])]

    def file_path(self, request, response=None, info=None):
        return request.meta['store'] + '/img/' + request.meta['image_name'] + '.jpg'
