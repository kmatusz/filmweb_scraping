# Main script for running friends and movies part
# Author Kamil Matuszelański

from selenium_funs import remove_csv, initialize_driver, scrape_friends, scrape_users_movies 
import pandas as pd

run_params = {
    # Facebook credentials
    # if wrong credentials will be passed, scraper will work
    # however number of pages will be limited
    'email': 'xxxxxx',
    'pwd': 'xxxxxx',
    # It is impossible to tell how many pages will be scraped as this depends on number of movies
    # Particular user rated
    # For reasonable time of running we recommend setting this to 5
    # It is potentially possible to scrape all users of filmweb accidentally
    'limit_users_to_scrape': 2
}

remove_csv(path = 'movies.csv')
print('initializing driver')

driver = initialize_driver(headless = True, email=run_params['email'], pwd=run_params['pwd'])


print('scraping friends')
# users = ['Kamilmac', 'greyshh']
users = scrape_friends(driver,max_friends=run_params['limit_users_to_scrape'], dump_to_csv=False)

users = users[:run_params['limit_users_to_scrape']]

print('scraping movies ratings')
movies = scrape_users_movies(driver, users = users, dump_to_csv=True, path = 'movies.csv')

print('quitting')
driver.quit()

