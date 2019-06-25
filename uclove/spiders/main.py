# -*- coding: utf-8 -*-
import scrapy


class MainSpider(scrapy.Spider):
    name = 'main'
    allowed_domains = ['mobile.facebook.com']
    start_urls = ['https://mobile.facebook.com/uclove/']

    def parse(self, response):
        pass
