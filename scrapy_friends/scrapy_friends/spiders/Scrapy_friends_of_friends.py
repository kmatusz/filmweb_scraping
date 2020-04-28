import scrapy

class Movieff(scrapy.Item):
    ffriends_links = scrapy.Field()

class MovieSpider(scrapy.Spider):
    name = 'ffriends'
    allowed_domains = ['www.filmweb.pl']
    try:
        with open("friends.csv", "rt") as f:
            start_urls = [url.strip() for url in f.readlines()][1:]
    except:
        start_urls = []

    def parse(self, response):
        #print(response)
        xpath_f = '//ul[re:test(@class, "userBoxes__list")]//li//@data-user-name'
        selection = response.xpath(xpath_f)
        for s in selection:
            l = Movieff()
            l['ffriends_links'] ='http://www.filmweb.pl/user/' + s.get() + '/friends'
            print(l)
            yield l