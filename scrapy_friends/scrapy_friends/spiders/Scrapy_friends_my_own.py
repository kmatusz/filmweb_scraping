import scrapy

class Movief(scrapy.Item):
    friends_links = scrapy.Field()

class MovieSpider(scrapy.Spider):
    name = 'friends'
    allowed_domains = ['www.filmweb.pl']
    start_urls = ['http://www.filmweb.pl/user/Dr_Marvel/friends']

    def parse(self, response):
        xpath_friends = '//ul[re:test(@class, "userBoxes__list")]//li//@data-user-name'
        selection = response.xpath(xpath_friends)
        for s in selection:
            l = Movief()
            l['friends_links'] = 'http://www.filmweb.pl/user/' + s.get() + '/friends'
            yield l
#działa poprawnie