from selenium import webdriver
import time
import getpass
import datetime
import json
import pandas as pd
import os



from selenium_funs import *

driver = initialize_driver()
driver

pagination_url('Kamilmac', 1)


driver.get(pagination_url('Kamilmac', 1))
boxes = get_boxes(driver)
get_movie(boxes[1])

driver.get(pagination_url('Kamilmac', 1))
movies = scrape_page(driver)
movies[0]


movies = scrape_user(driver, 'Kamilmac')


print(len(movies))
movies[-4]

movies

scrape_users(driver, users = ['Kamilmac'], dump_to_csv=True)


import pandas as pd


remove_csv()


movies


driver.quit()


# #### Todo:
# 
# - czyszczenie csv
# - zapisanie outputu jako csv
# - get_users (z csv/listy)
# - scrape_users

