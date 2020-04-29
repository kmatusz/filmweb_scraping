#Importing library
import scrapy

#Defining class
class Movief(scrapy.Item):
    friends_links = scrapy.Field()

#Defining class (name to execute program + allowed domain and starting URL)
class MovieSpider(scrapy.Spider):
    name = 'friends'
    allowed_domains = ['www.filmweb.pl']
    start_urls = ['http://www.filmweb.pl/user/Dr_Marvel/friends']

    #getting friends of your own, links to their friends, which will be helpful in next level of friends (iteration)
    def parse(self, response):
        xpath_friends = '//ul[re:test(@class, "userBoxes__list")]//li//@data-user-name'
        selection = response.xpath(xpath_friends)
        for s in selection:
            l = Movief()
            l['friends_links'] = 'http://www.filmweb.pl/user/' + s.get() + '/friends'
            yield l
