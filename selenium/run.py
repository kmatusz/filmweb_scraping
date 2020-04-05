from selenium_funs import *
import pandas as pd

remove_csv()

driver = initialize_driver(headless = True)

# users = get_users() 
users = ['Kamilmac', 'greyshh']

movies = scrape_users(driver, users = users, dump_to_csv=True, path = 'movies.csv')

driver.quit()

