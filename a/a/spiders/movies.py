# -*- coding: utf-8 -*-
import scrapy
import json

class Movie(scrapy.Item):
    movie_title = scrapy.Field()
    movie_year = scrapy.Field()
    movie_rating_no = scrapy.Field()
    movie_id = scrapy.Field()
    movie_rating_avg = scrapy.Field()
    
    user_rated_year = scrapy.Field()
    user_rated_month = scrapy.Field()
    user_rated_day = scrapy.Field()
    user_rating = scrapy.Field()
    user_url = scrapy.Field() 
    
    
def get_users_to_scrape():
    return ['Kamilmac', 'greyshh', 'dsfajeglwejgwgjwww']

def get_urls_to_scrape():
    users = get_users_to_scrape()
    
    return [f'https://www.filmweb.pl/user/{user}/films' for user in users]

class MovieSpider(scrapy.Spider):
    name = 'movies'
    allowed_domains = ['www.filmweb.pl']
    
    start_urls = get_urls_to_scrape()
        
    def parse(self, response):
        
        user_rating_data = self._parse_user_ratings(response)
        
        xpath_boxes = '//div[@class="myVoteBox "]'
        selection = response.xpath(xpath_boxes)
        
        xpath_title = './div[@class = "myVoteBox__top"]//h3[@class="filmPreview__title"]/text()' # tytuł
        xpath_year = './div[@class = "myVoteBox__top"]//span[@class="filmPreview__year"]/text()' #rok
        xpath_rating_avg = './div[@class = "myVoteBox__top"]//span[@class="rateBox__rate"]/text()' #ocena
        xpath_rating_no = './div[@class = "myVoteBox__top"]//span[@class="rateBox__votes rateBox__votes--count"]/text()' # liczba ocen
        
        xpath_movie_id = './/*[@data-id]/@data-id' # Id filmu do wykorzystania z joinem do ocen

        for s in selection:
            
            movie = Movie()
            
            movie_id              = s.xpath(xpath_movie_id).get()
            
            movie['movie_title']         = s.xpath(xpath_title).get()
            movie['movie_year']          = s.xpath(xpath_year).get()
            movie['movie_rating_avg']    = s.xpath(xpath_rating_avg).get()
            movie['movie_id']      = movie_id
            movie['movie_rating_no']     = s.xpath(xpath_rating_no).get()

            
            for field, value in user_rating_data[movie_id].items():
                movie[field] = value
                
            movie['user_url']   = response.url

            yield movie
            
            
    def _parse_user_ratings(self, response):
        
        
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
    
