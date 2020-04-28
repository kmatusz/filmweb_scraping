# -*- coding: utf-8 -*-
import scrapy


class MovieSpider(scrapy.Spider):
    name = 'movie'
    allowed_domains = ['http://filmweb.pl']
    start_urls = ['http://http://filmweb.pl/']

    def parse(self, response):
        pass
