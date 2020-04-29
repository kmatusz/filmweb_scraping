import scrapy

# What we want to scrap (usernames of friends of friends of own friends)
#Some extra information is commented, because it isn't necessary in case of this task
class Moviefff(scrapy.Item):
    username = scrapy.Field()
    # name = scrapy.Field()
    # surname = scrapy.Field()
    # url = scrapy.Field()

# Where we want to scrap (from before created csv file in output of Scrapy_friends_of_friends.py) by using option "-o" in scrapy crawl
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

    # How to scrap usernames of third level friendship (friends of friends of friends)
    #Function return dictionary in column username with usernames of friends in filmweb.pl page
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
