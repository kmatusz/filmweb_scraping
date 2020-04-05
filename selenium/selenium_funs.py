from selenium import webdriver
import time
import getpass
import datetime
import json
import pandas as pd
import os


def scrape_users(driver, users, dump_to_csv = True, path = 'movies.csv'):

    movies = []

    for user in users:
        print(f'Scraping user: {user}')

        new_movies = scrape_user(driver, user)

        if dump_to_csv:
            dump_movies_to_csv(new_movies, path)
        else:
            movies = movies + new_movies
    
    return movies

def get_users():
    return ['Kamilmac', 'greyshh']


def scrape_user(driver, name):
    movies = []
    
    page_no = 1
    while True:
        print(f'Obtaining page {page_no}')
        driver.get(pagination_url(name, page_no))
        
        new_movies = scrape_page(driver)
        is_friend = check_if_friend(driver)

        movies = movies + new_movies
        page_no += 1

        if len(new_movies) == 0 or not is_friend:
            print('No more movies')
            break
        
        
    for movie in movies:
        movie['user'] = name
    
    return movies

def check_if_friend(driver):
    try:
        driver.find_element_by_xpath('//a[contains(@class, "BefriendButton")]')
    except:
        return True
    
    print('Not friend')
    return False


def dump_movies_to_csv(movies, path = 'movies.csv'):
    df = pd.DataFrame(movies)

    if os.path.exists(path):
        df.to_csv(path, mode='a', header=False)
    else: 
        df.to_csv(path)



def remove_csv(path = 'movies.csv'):
    if os.path.exists(path):
        os.remove(path)

def pagination_url(user, page_no):
    return f'https://www.filmweb.pl/user/{user}/films?page={page_no}'

def scrape_page(driver):
    
    boxes = get_boxes(driver)
    
    movies = []
    
    for i, box in enumerate(boxes):
        # print(f'obtaining box {i}')
        movies.append(get_movie(box))
        
    return movies

def get_boxes(driver):
    xpath_boxes = '//div[@class="myVoteBox "]'

    return driver.find_elements_by_xpath(xpath_boxes)

def get_movie(box):
    
    xpath_title = './div[@class = "myVoteBox__top"]//h3[@class="filmPreview__title"]' # tytuł
    xpath_year = './div[@class = "myVoteBox__top"]//span[@class="filmPreview__year"]' #rok
    xpath_rating_avg = './div[@class = "myVoteBox__top"]//span[@class="rateBox__rate"]' #ocena
    xpath_rating_no = './div[@class = "myVoteBox__top"]//span[@class="rateBox__votes rateBox__votes--count"]' # liczba ocen

    xpath_movie_id = './/*[@data-id]' # Id filmu do wykorzystania z joinem do ocen

    xpath_date = './/div[@class = "voteCommentBox__date"]' # Data oceny po polsku [sic!]
    xpath_user_rating = './/span[@class = "userRate__rate"]' # ocena
    
    movie = {}

    movie_id                     = box.find_element_by_xpath(xpath_movie_id).get_attribute('data-id')
    movie['movie_title']         = box.find_element_by_xpath(xpath_title).text
    movie['movie_year']          = box.find_element_by_xpath(xpath_year).text
    movie['movie_rating_avg']    = box.find_element_by_xpath(xpath_rating_avg).text
    movie['movie_rating_no']     = box.find_element_by_xpath(xpath_rating_no).text
    movie['user_rated_date']     = box.find_element_by_xpath(xpath_date).text
    movie['user_rating']         = box.find_element_by_xpath(xpath_user_rating).text
    
    movie['movie_id']            = movie_id
    
    return movie
    
    

def initialize_driver(email = None, pwd = None, headless = False):
    driver = login_with_fb(email, pwd, headless = headless)

    time.sleep(5)
    driver = click_popups(driver)
    
    print('driver initialized')
    return driver


def login_with_fb(email = None, pwd = None, headless = False):
    
    if email is None or pwd is None:
        email = input('Please provide your email:')
        pwd = getpass.getpass('Please provide your password:')
    
    url = 'https://www.filmweb.pl/fbc/entryPoint?_login_redirect_url=https://www.filmweb.pl/'

    options = webdriver.firefox.options.Options()
    options.headless = headless

    driver = webdriver.Firefox(options = options)

    driver.get(url)
    
    print('Fb loaded')
    
    username = driver.find_element_by_xpath('//input[@id = "email"]')
    username.send_keys(email)
    
    password = driver.find_element_by_xpath('//input[@id="pass"]')
    password.send_keys(pwd)
    
    button = driver.find_element_by_xpath('//button[@id = "loginbutton"]')
    button.click()
    
    print('Logged in')
    
    return driver
    
def click_popups(driver):
    # Commercial
    try:
        xpath = '//button[@class = "ws__skipButton"]'

        button = driver.find_element_by_xpath(xpath)
        button.click()
    except:
        pass
    
    # RODO
    try:
        xpath = '//button[text() = "Rozumiem"]'

        button = driver.find_element_by_xpath(xpath)
        button.click()
    except:
        pass
    
    return driver

