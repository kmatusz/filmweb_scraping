# -*- coding: utf-8 -*-
import scrapy
import json
import re
from const import run_params
    
class MovieSpider(scrapy.Spider):
    # Scrape movies from consecutive users
    name = 'movies'
    allowed_domains = ['www.filmweb.pl']

    def start_requests(self):
        # This is equivalent to start_urls, but allows for passing arguments (cookies)
        # To request
        # It yields first page per user and sends the request to parse function
        urls = get_urls_to_scrape()

        self._setup_constants()

        for url in urls:
            yield scrapy.Request(
                url=url, 
                callback=self.parse, 
                cookies=self.cookies,  
                meta={'dont_merge_cookies': False},
                headers=self.headers,
                cb_kwargs={'current_url': url}
                )

    def _setup_constants(self):
        # Set up cookie magic for faking authentcation
        # Load cookies from previously created (in login scraper) 

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
            'Accept': 'text/css,*/*;q=0.1',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3'
            }
        
        # Parameter whether to try logging in.
        #  Without logged in user the scraper still works, 
        # but scrapes limited number of pages
        self.try_login = run_params['try_login']
        
        if self.try_login:
            self.cookies = load_cookie_json()
        else:
            self.cookies = {}

        self.limit_pages_per_user = run_params['limit_pages_per_user']

        
    def parse(self, response, current_url):

        # in boxes there are multiple boxes, one for each movie on a page
        boxes = self._extract_movies_boxes(response)

        # Set up a flag for the website when it's empty 
        # (we hit number of movies avaliable through pagination)
        empty_page_flag = self._check_if_non_zero_movies(boxes)

        # Users for whom logged in user is not friend with does not have 
        # 'go to next page' button
        if not self._check_if_friend(response):
            empty_page_flag = True

        # User ratings for full page are hidden in json in page source
        # It requires special treatment othere than scraping movie information
        # (title, year of production etc.)
        user_rating_data = self._parse_user_ratings(response)
        

        # Iterate through each box and obtain avaliable movie info
        for box in boxes:
            yield self._parse_one_movie(box, user_rating_data, response.url)

        
        if_abort_user = self._check_if_abort(current_url)

        if not empty_page_flag and not if_abort_user:
            print('Going to the next page')

            # Yield next page from particular user to scrape 
            yield scrapy.Request(
                url=next_page_url(current_url), 
                callback=self.parse, 
                cookies=self.cookies,  
                meta={'dont_merge_cookies': False},
                headers=self.headers,
                cb_kwargs={'current_url': next_page_url(current_url)}
                ) 

    def _parse_user_ratings(self, response):
        # Parse data about user ratings stored as json
        xpath_data = '//span[@class = "dataSource hide"]//script/text()'
        
        jsons = response.xpath(xpath_data)
        jsons = [x.get() for x in jsons]
        
        out_dict = {}
        
        for one_json in jsons:
            a = json.loads(one_json)
            temp = {
                'user_rated_year': a['d']['y'],
                'user_rated_month': a['d']['m'],
                'user_rated_day': a['d']['d'],
                'user_rating': a['r']
                }
            out = {str(a['eId']): temp}
                    
            out_dict.update(out)
            
        return out_dict

    def _extract_movies_boxes(self, response):
        xpath_boxes = '//div[@class="myVoteBox "]'
        return response.xpath(xpath_boxes)

    def _check_if_non_zero_movies(self, boxes):
        if len(boxes) == 0:
            empty_page_flag = True
            print('No movies on this page')
        else:
            empty_page_flag = False
        
        return empty_page_flag

    def _check_if_friend(self, response):
        if len(response.xpath('//li[@class="pagination__item "]//text()')) == 0:
            print('NO FRIEND')
            return False
        else:
            return True
           

    def _parse_one_movie(self, box, user_rating_data, url):

        # Set up xpaths for obtaining movie info
        movie_data_xpaths = {
            'title': './div[@class = "myVoteBox__top"]//h3[@class="filmPreview__title"]/text()', 
            'year': './div[@class = "myVoteBox__top"]//span[@class="filmPreview__year"]/text()', # year of movie
            'rating_avg': './div[@class = "myVoteBox__top"]//span[@class="rateBox__rate"]/text()', # mean rating from all users
            'rating_no': './div[@class = "myVoteBox__top"]//span[@class="rateBox__votes rateBox__votes--count"]/text()', # rating count
            'movie_id': './/*[@data-id]/@data-id' # internal id of the movie 
        }

        movie = Movie()
        
        movie_id                     = box.xpath(movie_data_xpaths['movie_id']).get()
        movie['movie_id']            = movie_id

        movie['movie_title']         = box.xpath(movie_data_xpaths['title']).get()
        movie['movie_year']          = box.xpath(movie_data_xpaths['year']).get()
        movie['movie_rating_avg']    = box.xpath(movie_data_xpaths['rating_avg']).get()
        movie['movie_rating_no']     = box.xpath(movie_data_xpaths['rating_no']).get()
        movie['user_url']            = url


        # Obtain rating data for particular movie (created earlier)
        for field, value in user_rating_data[movie_id].items():
            movie[field] = value

        return movie

    def _check_if_abort(self, current_url):
        # Function to check whether to stop iterating through pages

        if self.limit_pages_per_user is not None:
            if_abort = int(re.findall(r'\d+$', current_url)[0]) >= self.limit_pages_per_user
        
        else:
            if_abort = False

        # For running scraper without login only one page per user is possible
        if not self.try_login:
            if_abort = True

        if if_abort:
            print('Maximum number of pages per user scraped. Aborting')

        return if_abort
    

class Movie(scrapy.Item):
    # A class to contain one movie scraped. 
    movie_title = scrapy.Field()
    movie_year = scrapy.Field()
    movie_rating_no = scrapy.Field()
    movie_id = scrapy.Field()
    movie_rating_avg = scrapy.Field()
    
    user_rated_year = scrapy.Field()
    user_rated_month = scrapy.Field()
    user_rated_day = scrapy.Field()
    user_rating = scrapy.Field()
    user_url = scrapy.Field() # Url of website from which the movie was scraped


def get_users_to_scrape(limit_users_to_scrape = None):
    # Obtain file with friends output
    # Limit users to scrape can be set up from file const.py

    with open('data/friends.csv', 'r') as file:
        users = [i.rstrip() for i in file.readlines()]

    if limit_users_to_scrape is not None:
        return users[:limit_users_to_scrape]
    # return ['Kamilmac', 'greyshh', 'mateusz_andruszko', 'WozniaczekSlodziaczek', 'dsfajeglwejgwgjwww']
    return users


def get_urls_to_scrape():
    # Create valid urls from list of users. First url is set for page 1
    users = get_users_to_scrape(limit_users_to_scrape=run_params['limit_users_to_scrape'])
    
    return [f'https://www.filmweb.pl/user/{user}/films?page=1' for user in users]

def load_cookie_json():
    # Load cookies from file. (Cookies are obtained in login scraper)
    # Cookies enable authentication with facebook

    try:
        with open('cookies.json', 'r') as inputfile:
            print('cookies loaded')
            cookies = json.load(inputfile)
    except:
        cookies = {}
    return cookies

def next_page_url(url):
    # Return next paginated page
    # e.g. input: www.filmweb.pl/?page=1, output: www.filmweb.pl/?page=2 
    current = int(re.findall(r'\d+$', url)[0])
    return re.sub(r'\d+$', str(current+1), url)
