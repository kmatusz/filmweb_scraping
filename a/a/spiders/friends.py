# Contains scraper of user logins 
# Created by Kamil Matuszelański and Grzegorz Kowalczyk

import scrapy
import re

class Friend(scrapy.Item):
    user = scrapy.Field()
    page_scraped = scrapy.Field()


class FriendsSpider(scrapy.Spider):
    name = 'friends'
    allowed_domains = ['www.filmweb.pl']
    
    custom_settings = {
        'EXTENSIONS' : {
            'scrapy.extensions.closespider.CloseSpider': 10
        }
    }

    def start_requests(self):
        # This is equivalent to start_urls
        # It yields first page per user and sends the request to parse function
        urls = get_urls_to_scrape()

        for url in urls:
            yield scrapy.Request(
                url=url, 
                callback=self.parse, 
                meta={'dont_merge_cookies': False},
                cb_kwargs={'current_url': url}
                )

    

    def parse(self, response, current_url):

        # Scrape one page, save usernames from this page to a list
        current_usernames = []
        xpath_friends = '//ul[re:test(@class, "userBoxes__list")]//li//@data-user-name'
        selection = response.xpath(xpath_friends)

        for s in selection:
            # yield friend username and link from which friend was obtained 
            l = Friend()
            text = s.get()
            current_usernames.append(text)
            l['user'] = text
            l['page_scraped'] = current_url
            yield l


        if len(current_usernames) != 0:
            print('no usernames on this page. Aborting')
            # Yield next page from particular user to scrape (friends list is paginated)
            yield scrapy.Request(
                url=next_page_url(current_url), 
                callback=self.parse, 
                # cookies=self.cookies,  
                meta={'dont_merge_cookies': False},
                # headers=self.headers,
                cb_kwargs={'current_url': next_page_url(current_url)}
                )

        for i in current_usernames:
            # Go to next user (every user from current page)
            print('yielding next user:' + i)
            next_friend_url = f'https://www.filmweb.pl/user/{i}/friends?page=1'
            yield scrapy.Request(
                url=next_friend_url, 
                callback=self.parse, 
                # cookies=self.cookies,  
                meta={'dont_merge_cookies': False},
                # headers=self.headers,
                cb_kwargs={'current_url': next_friend_url}
                )

def next_page_url(url):
    # Return next paginated page
    # e.g. input: www.filmweb.pl/?page=1, output: www.filmweb.pl/?page=2 
    current = int(re.findall(r'\d+$', url)[0])
    return re.sub(r'\d+$', str(current+1), url)


def get_urls_to_scrape():
    # Get starting url from data/my_profile_url.txt file (created using login part) 
    try:
        with open('data/my_profile_url.txt') as file:
            my_profile_url = file.readlines()
        return [i + '/friends?page=1' for i in my_profile_url]
    except:
        return ['https://www.filmweb.pl/user/Kamilmac/friends?page=1']


