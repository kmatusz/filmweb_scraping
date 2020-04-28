import scrapy

# What we want to scrap
class Moviefff(scrapy.Item):
    username = scrapy.Field()
    # name = scrapy.Field()
    # surname = scrapy.Field()
    # url = scrapy.Field()

# Where we want to scrap
class MovieSpider(scrapy.Spider):
    name = 'fffriends'
    allowed_domains = ['www.filmweb.pl']
    try:
        with open("ffriends.csv", "rt") as f:
            start_urls = [url.strip() for url in f.readlines()][1:]
        print("*****************************")
        print("reading file worked")
        print("*****************************")
    except:
        start_urls = []
        print("*****************************")
        print("reading file did not work")
        print("*****************************")

    # How to scrap
    def parse(self, response):
        username_xpath = '//ul[@class="userBoxes__list"]//li//@data-user-name'
        # name_xpath = '//div[@class="userPreview userPreview__hasFullName"]//@data-f-name'
        # surname_xpath = '//div[@class="userPreview userPreview__hasFullName"]//@data-l-name'
        selection = response.xpath(username_xpath)
        for s in selection:
            p=Moviefff()
            p['username'] = s.get()
            # p['name'] = response.xpath(name_xpath).getall()
            # p['surname'] = response.xpath(surname_xpath).getall()
            # p['url'] = response.request.url
            yield p

#     # How to scrap
#     def parse(self, response):
#         username_xpath = '//ul[@class="userBoxes__list"]//li//@data-user-name'
#         selection = response.xpath(username_xpath)
#         p = Moviefff()
#         for s in selection:
#             p['username'] = s.get()
#             if p not in self.lista:
#                 print("lista: ", self.lista, "p: ", p)
#                 self.lista.append(p)
#                 yield p