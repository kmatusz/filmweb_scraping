from selenium import webdriver
import time
import getpass
import datetime
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt


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
    time.sleep(2)
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
    button = driver.find_element_by_xpath('//button[@class="popupForm__button authButton authButton--submit materialForm__submit"]')
    button.click()
    time.sleep(1)
    print("************************\nAfter logging in\n*********\n")


def skip_ad(driver):
    time.sleep(3)
    try:
        button = driver.find_element_by_xpath('//button[@class="ws__skipButton"]')
    except:
        button = driver.find_element_by_xpath('//button[@class="ws__skipButton ws__skipButton--inactive"]')
    button.click()
    time.sleep(1)
    print("************************\nAfter ad:\n*********\n")


def get_my_profile_url(driver):
    time.sleep(3)
    button = driver.find_element_by_id("userHeaderButton")
    button.click()
    time.sleep(1)
    print("************************\nAfter clicking on user account\n*********\n")

    return driver.current_url


def retrive_friends(driver, url):
    new_url = url + '/friends'
    driver.get(new_url)
    time.sleep(1)

    scroll_to_bottom(driver)
    button = driver.find_elements_by_xpath('//ul[@class="userBoxes__list"]/li')
    friends_set = set(button)

    number_friends = (len(friends_set))

    return number_friends, [friend.get_attribute("data-user-name") for friend in friends_set]


def get_profile_url(username):
    profile_url = 'http://www.filmweb.pl/user/' + str(username)
    return profile_url


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


def histogram(data):
    plt.hist(data, rwidth=0.9, color='#607c8e', label=True)
    plt.title("Distribution of friends count in the sample")
    plt.xlabel('Number of friends')
    plt.ylabel('Number of users')
    plt.show()


def main():
    url = 'http://www.filmweb.pl/login'
    parameter = 100

    driver = connect(url)
    accept_RODO(driver)
    login(driver)
    if driver.find_elements_by_class_name("ws__countdown"):
        skip_ad(driver)
    profile_url = get_my_profile_url(driver)

    my_friends_set = set(retrive_friends(driver, profile_url)[1])
    all_friends_df = add_usernames(parameter, my_friends_set, driver)
    print(all_friends_df)
    remove_csv()
    dump_movies_to_csv(all_friends_df)
    histogram(all_friends_df.loc[:, 'Number of friends'])
    time.sleep(3)
    driver.quit()


if __name__ == "__main__":
    main()