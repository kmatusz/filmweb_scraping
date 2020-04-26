from selenium import webdriver
import time
import getpass
import datetime
import json
import pandas as pd
import os

# Scraping movies part - author Kamil Matuszelański

def scrape_users_movies(driver, users, dump_to_csv = True, path = 'movies.csv'):
    # Scrape movies ratings for each user in the list
    # optionally save output to csv
    
    movies = []

    for user in users:
        print(f'Scraping user: {user}')

        new_movies = scrape_user_movies(driver, user)

        if dump_to_csv:
            dump_df_to_csv(new_movies, path)
        else:
            movies = movies + new_movies
    
    return movies


def scrape_user_movies(driver, name):
    # Scrape movies ratings for one user
    movies = []
    
    page_no = 1
    while True:
        # User ratings are paginated 
        # Obtaining next page until there are no more movies on a page
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
    # Check if particular user is a friend to a logged in user 
    # Useful in obtaining list for movies 
    try:
        driver.find_element_by_xpath('//a[contains(@class, "BefriendButton")]')
    except:
        return True
    
    print('Not friend')
    return False


def dump_df_to_csv(movies, path = 'movies.csv'):
    # save a dataframe to csv 
    # if csv already exists append
    df = pd.DataFrame(movies)

    if os.path.exists(path):
        df.to_csv(path, mode='a', header=False)
    else: 
        df.to_csv(path)



def remove_csv(path = 'movies.csv'):
    # remove file if exists
    if os.path.exists(path):
        os.remove(path)

def pagination_url(user, page_no):
    # return valid pagination url
    return f'https://www.filmweb.pl/user/{user}/films?page={page_no}'

def scrape_page(driver):
    # Scrape contents of one page (movies ratings)
    # On each page there are multiple boxes. One box - one movie

    boxes = get_boxes(driver)
    
    movies = []
    
    for i, box in enumerate(boxes):
        # print(f'obtaining box {i}')
        movies.append(get_movie(box))
        
    return movies

def get_boxes(driver):
    # extract boxes from a page
    xpath_boxes = '//div[@class="myVoteBox "]'

    return driver.find_elements_by_xpath(xpath_boxes)

def get_movie(box):
    # Obtain movie info from one box (all details)
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
    
    
# Driver initialization part - author Kamil Matuszelański
def initialize_driver(email = None, pwd = None, headless = False):
    # Start driver, login with facebook and hide popups obscuring the page
    driver = login_with_fb(email, pwd, headless = headless)

    time.sleep(5)
    driver.get('https://www.filmweb.pl/')
    
    driver = click_popups(driver)
    
    print('driver initialized')
    return driver


def login_with_fb(email = None, pwd = None, headless = False):
    # Run login
    # If not logged in, scraper will still work
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
    # CLick on popups butons to hide them 

    # Commercials 
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

# Scraping friends part - author Grzegorz Kowalczyk

def scrape_friends(driver, max_friends = 1, dump_to_csv = False, path= 'friends.csv'):
    # main function for scraping friends
    print('running friends part')
    url = 'http://www.filmweb.pl/login'

    profile_url = get_my_profile_url(driver)

    my_friends_set = set(retrive_friends(driver, profile_url)[1])
    all_friends_df = add_usernames(max_friends, my_friends_set, driver)
    temp1 = list(all_friends_df['Username'])
    temp2 = sum(list(all_friends_df['List of friends']), [])
    users = temp1 + temp2

    if dump_to_csv:
        remove_csv(path)
        dump_df_to_csv(all_friends_df, path = path)
    
    return users



def get_profile_url(username):
    profile_url = 'http://www.filmweb.pl/user/' + str(username)
    return profile_url

# def histogram(data):
#     plt.hist(data, rwidth=0.9, color='#607c8e', label=True)
#     plt.title("Distribution of friends count in the sample")
#     plt.xlabel('Number of friends')
#     plt.ylabel('Number of users')
#     plt.show()


def get_my_profile_url(driver):
    time.sleep(3)
    try:
        button = driver.find_element_by_id("userHeaderButton")
        button.click()
        time.sleep(1)
        return driver.current_url
    except:
        print('not logged in')
        print('returning random user url')
        return 'https://www.filmweb.pl/user/Kamilmac'
    
    

def retrive_friends(driver, url):
    # print('obtaining first user friends')

    new_url = url + '/friends'
    driver.get(new_url)
    time.sleep(1)

    scroll_to_bottom(driver)
    button = driver.find_elements_by_xpath('//ul[@class="userBoxes__list"]/li')
    friends_set = set(button)

    number_friends = (len(friends_set))

    return number_friends, [friend.get_attribute("data-user-name") for friend in friends_set]

def scroll_to_bottom(driver):

    old_position = 0
    new_position = None

    while new_position != old_position:
        # Get old scroll position
        old_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                 " window.pageYOffset : (document.documentElement ||"
                 " document.body.parentNode || document.body);"))
        # Sleep and Scroll
        time.sleep(1)
        driver.execute_script((
                "var scrollingElement = (document.scrollingElement ||"
                " document.body);scrollingElement.scrollTop ="
                " scrollingElement.scrollHeight;"))
        # Get new position
        new_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                 " window.pageYOffset : (document.documentElement ||"
                 " document.body.parentNode || document.body);"))

def add_usernames(parameter, friends_set, driver):
    dfObj = pd.DataFrame(columns=['Username', 'Number of friends', 'List of friends'])
    friend_friends = set()
    ffriend_friends = set()
    for friend in friends_set:
        if (len(dfObj) < parameter):
            friend_url = get_profile_url(friend)
            number_of_friends, list_of_friends = retrive_friends(driver, friend_url)
            friend_df = pd.DataFrame({'Username': friend, 'Number of friends': number_of_friends, 'List of friends': [list_of_friends]})
            dfObj= dfObj.append(friend_df)
            for element in list_of_friends:
                friend_friends.add(element)
        else:
            break
    print("************************\nMy friends\n*********\n")

    for guy in list(friend_friends):
        if ((not(any(dfObj['Username'] == guy))) and (len(dfObj) < parameter)):
            ffriend_url = get_profile_url(guy)
            number_of_friends, list_of_friends = retrive_friends(driver, ffriend_url)
            friend_df = pd.DataFrame({'Username': guy, 'Number of friends': number_of_friends, 'List of friends': [list_of_friends]})
            dfObj = dfObj.append(friend_df)
            for element in list_of_friends:
                ffriend_friends.add(element)
        else:
            break
    print("************************\nMy friends' friends\n*********\n")

    for guy in list(ffriend_friends):
        if ((not(any(dfObj['Username'] == guy))) and (len(dfObj) < parameter)):
            ffriend_url = get_profile_url(guy)
            number_of_friends, list_of_friends = retrive_friends(driver, ffriend_url)
            friend_df = pd.DataFrame({'Username': guy, 'Number of friends': number_of_friends, 'List of friends': [list_of_friends]})
            dfObj = dfObj.append(friend_df)
            for element in list_of_friends:
                ffriend_friends.add(element)
        else:
            break
    print("************************\nMy friends' friends of friends\n*********\n")

    return dfObj
