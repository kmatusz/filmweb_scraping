from selenium import webdriver
import time
import getpass
import datetime
import pandas as pd
import os


def connect(url):
    options = webdriver.firefox.options.Options()
    options.headless = True
    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.implicitly_wait(30)
    driver.get(url)

    print("************************\nAfter connecting to the website\n*********\n")
    return driver


# Accepting RODO police
def accept_RODO(driver):
    button = driver.find_element_by_xpath('//button[@class="fwBtn fwBtn--gold"]')
    button.click()
    time.sleep(2)

    print("************************\nAfter accepting RODO\n*********\n")


def login(driver):
    # login with filmweb account
    button = driver.find_element_by_xpath('//div[@class="authPage__button authButton authButton--filmweb"]')
    button.click()
    time.sleep(1)
    print("************************\nAfter choosing way of logging in\n*********\n")

    # provide credentials
    username_field = driver.find_element_by_xpath('//input[@name="j_username"]')
    my_email = input('Please provide your email:')
    username_field.send_keys(my_email)
    time.sleep(1)

    password_field = driver.find_element_by_xpath('//input[@name="j_password"]')
    my_pass = getpass.getpass('Please provide your password:')

    password_field.send_keys(my_pass)
    time.sleep(1)

    # accept the credentials
    button = driver.find_element_by_xpath(
        '//button[@class="popupForm__button authButton authButton--submit materialForm__submit"]')
    button.click()

    print("************************\nAfter logging in\n*********\n")


def skip_ad(driver):
    button = driver.find_element_by_xpath('//button[@class="ws__skipButton"]')
    button.click()
    time.sleep(1)

    print("************************\nAfter ad:\n*********\n")


def get_my_profile_url(driver):
    button = driver.find_element_by_id("userHeaderButton")
    button.click()
    time.sleep(1)
    print("************************\nAfter clicking on user account\n*********\n")

    return driver.current_url


def retrive_friends(driver, url):
    new_url = url + '/friends'
    driver.get(new_url)
    time.sleep(0.7)

    scroll(driver, 0.7)
    time.sleep(0.7)
    button = driver.find_elements_by_xpath('//ul[@class="userBoxes__list"]/li')
    friends_set = set(button)

    return [friend.get_attribute("data-user-name") for friend in friends_set]


def get_profile_url(username):
    profile_url = 'http://www.filmweb.pl/user/' + str(username)
    return profile_url


def scroll(driver, timeout):
    scroll_pause_time = timeout

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same it will exit the function
            break
        last_height = new_height


def dump_movies_to_csv(movies, path='friends.csv'):

    df = pd.DataFrame(movies)

    if os.path.exists(path):
        df.to_csv(path, mode='a', header=False, index=False)
    else:
        df.to_csv(path, header=False, index=False)


def remove_csv(path='friends.csv'):
    if os.path.exists(path):
        os.remove(path)


def add_usernames(parameter, friends_set, driver):
    all_friends_set = set()
    friend_friends = set()
    ffriend_friends = set()

    print("************************\nMy friends\n*********\n")
    for friend in friends_set:

        if (len(all_friends_set) < parameter):
            all_friends_set.add(friend)
            friend_url = get_profile_url(friend)
            [friend_friends.add(f) for f in retrive_friends(driver, friend_url)]
        else:
            break

    print("************************\nMy friends' friends\n*********\n")
    for guy in list(friend_friends):
        if (len(all_friends_set) < parameter):
            all_friends_set.add(guy)
            ffriend_url = get_profile_url(guy)
            [ffriend_friends.add(f) for f in retrive_friends(driver, ffriend_url)]
        else:
            break

    print("************************\nMy friends' friends of friends\n*********\n")
    for guys in list(ffriend_friends):
        if (len(all_friends_set) < parameter):
            all_friends_set.add(guys)
        else:
            break
    return all_friends_set


def main():
    url = 'http://www.filmweb.pl/login'
    parameter = 1000

    driver = connect(url)
    accept_RODO(driver)
    login(driver)
    if driver.find_elements_by_class_name("ws__countdown"):
        skip_ad(driver)
    profile_url = get_my_profile_url(driver)

    friends_set = set(retrive_friends(driver, profile_url))
    all_friends_set = add_usernames(parameter, friends_set, driver)

    remove_csv()
    dump_movies_to_csv(all_friends_set)
    time.sleep(3)
    driver.quit()

if __name__ == "__main__":
    main()