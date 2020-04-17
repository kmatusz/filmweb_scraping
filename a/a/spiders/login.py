# Contains scraper of facebook login page.
# Created by Kamil Matuszelański

import scrapy
import json
from scrapy_selenium import SeleniumRequest
import time
from const import run_params

class LoginSpider(scrapy.Spider):
    # This spider is a trick for logging in
    # It uses scrapy_selenium package to login (using JS),
    # And then saves all session cookies to json file
    # This json is then avaliable in vanilla scrapy movies spider.

    name = 'login'
    allowed_domains = ['www.filmweb.pl']

    # To enable selenium
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES' : {
            'scrapy_selenium.SeleniumMiddleware': 800
        },
        'SELENIUM_DRIVER_ARGUMENTS': ['-headless']
        # 'SELENIUM_DRIVER_ARGUMENTS'= [] # To use with browser enabled 
    }

    def start_requests(self):
        # Setup facebook login authentication - redirect to fb page
        url = 'https://www.filmweb.pl/fbc/entryPoint?_login_redirect_url=https://www.filmweb.pl/'

        yield SeleniumRequest(
            url=url, 
            callback=self.parse, 
            meta={'dont_merge_cookies': False}
            )
    
        
    def parse(self, response):
        # Function for sending credentials to facebook and logging in
        driver = response.request.meta['driver']

        print('Fb loaded')

        email = [run_params['email']]
        pwd = [run_params['pwd']]

        username = driver.find_element_by_xpath('//input[@id = "email"]')
        username.send_keys(email)
        
        password = driver.find_element_by_xpath('//input[@id="pass"]')
        password.send_keys(pwd)
        
        button = driver.find_element_by_xpath('//button[@id = "loginbutton"]')
        button.click()
    
        print('Logged in')


        cookies = driver.get_cookies()

        with open('data/cookies.json', 'w') as file:
            json.dump(cookies, file)
        print('Cookies saved')

        yield None

