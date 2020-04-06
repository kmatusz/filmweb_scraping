from selenium import webdriver
import time
import getpass
import datetime

def connect(url):
    options = webdriver.firefox.options.Options()
    options.headless = False
    driver = webdriver.Firefox()
    driver.implicitly_wait(30)
    driver.get(url)
    
    print("************************\nAfter connecting to the website\n*********\n")
    return driver

#Accepting RODO police
def accept_RODO(driver):
    button = driver.find_element_by_xpath('//button[@class="fwBtn fwBtn--gold"]')
    button.click()
    time.sleep(2)

    print("************************\nAfter accepting RODO\n*********\n")

def login(driver):
    #login with filmweb account
    button = driver.find_element_by_xpath('//div[@class="authPage__button authButton authButton--filmweb"]')
    button.click()
    time.sleep(2)
    print("************************\nAfter choosing way of logging in\n*********\n")

    #provide credentials
    username_field = driver.find_element_by_xpath('//input[@name="j_username"]')
    my_email = input('Please provide your email:')
    username_field.send_keys(my_email)
    time.sleep(2)

    password_field = driver.find_element_by_xpath('//input[@name="j_password"]')
    my_pass = getpass.getpass('Please provide your password:')
    password_field.send_keys(my_pass)
    time.sleep(2)

    #accept the credentials
    button = driver.find_element_by_xpath('//button[@class="popupForm__button authButton authButton--submit materialForm__submit"]')
    button.click()

    print("************************\nAfter logging in\n*********\n")


def skip_ad(driver):
    button = driver.find_element_by_xpath('//button[@class="ws__skipButton"]')
    button.click()
    time.sleep(3)

    print("************************\nAfter ad:\n*********\n")

def get_my_profile_url(driver):
    button = driver.find_element_by_xpath('//span[@class="user__name-wrap"]')
    button.click()
    time.sleep(3)
    print("************************\nAfter clicking on user account\n*********\n")
    return driver.current_url
 

def retrive_friends(driver, url):
    new_url = url + '/friends'
    driver.get(new_url)
    time.sleep(1)

    button = driver.find_elements_by_xpath('//ul[@class="userBoxes__list"]/li')
    friends_set = set(button)
    print("************************\nAfter retriving_friends\n*********\n")
    return [friend.get_attribute("data-user-name") for friend in friends_set]

def get_profile_url(username):
    profile_url = 'http://www.filmweb.pl/user/' + str(username)
    return profile_url


def main():
    url = 'http://www.filmweb.pl/login'

    driver = connect(url)
    accept_RODO(driver)
    login(driver)
    skip_ad(driver)
    profile_url = get_my_profile_url(driver)
    
    all_friends_set = set()
    friends_set = retrive_friends(driver, profile_url)

    for friend in friends_set:
        all_friends_set.add(friend)
    
        friend_url = get_profile_url(friend)
        friend_friends = retrive_friends(driver, friend_url)

        for guy in friend_friends:
            all_friends_set.add(guy)

    print(all_friends_set)
    time.sleep(1000)
    driver.quit()

if __name__ == "__main__":
    main()