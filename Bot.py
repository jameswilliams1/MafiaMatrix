from selenium import webdriver
from time import sleep
from selenium.common.exceptions import StaleElementReferenceException, InvalidSelectorException, ElementNotVisibleException, WebDriverException, NoSuchElementException, JavascriptException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys
import os
from random import randrange
import requests


def rand(min_time, max_time):
    """
    Returns random time interval between min and max seconds to 3 d.p.
    :param min_time:
    :param max_time:
    :return: time:
    """
    return min_time + randrange(0, (max_time-min_time) * 1000) / 1000


# Get exisiting user profile to help with captchas (not bypass)
def get_profile_path(profile):
    FF_PROFILE_PATH = os.path.join(os.environ['APPDATA'],'Mozilla', 'Firefox', 'Profiles')

    try:
        profiles = os.listdir(FF_PROFILE_PATH)
    except WindowsError:
        print("Could not find profiles directory.")
        sys.exit(1)
    try:
        for folder in profiles:
            #print(folder)
            if folder.endswith(profile):
                loc = folder
    except StopIteration:
        print("Firefox profile not found.")
        sys.exit(1)
    return os.path.join(FF_PROFILE_PATH, loc)


def delayType(el, text):
    for character in text:
        el.send_keys(character)
        sleep(rand(1, 3)/10) # pause for 0.1 - 0.3 s

#profile = get_profile_path("default")
profile = webdriver.FirefoxProfile()
email = ""
password = ""
API_KEY = 'f0586fa5c51758d7c32c5017c70a00fa'  # Your 2captcha API KEY
site_key = '6LeLBQwTAAAAAEjOl7RVSY-x9mxPOxSOSkkR24aY'  # site-key, read the 2captcha docs on how to get this
url = 'https://mafiamatrix.com/'  # example url
#proxy = '127.0.0.1:6969' # example proxy
s = requests.Session()

try:
    with open('login.txt', 'r') as f:
        email = f.readline()
        password = f.readline()
except IOError:
    email = input('Enter email:')
    password = input('Enter password')
    with open('login.txt', 'w') as f:
        f.write(email + '\n' + password)



def fill_log_in(driver):
    sleep(rand(2, 5))
    # Enter login
    email_field = driver.find_element_by_xpath('//*[@id="email"]')
    delayType(email_field, email)
    sleep(rand(2, 4))
    pass_field = driver.find_element_by_xpath('//*[@id="pass"]')
    delayType(pass_field, password)
    sleep(rand(3, 5))


def solve_captcha(driver, url, API_KEY, site_key):
    # post site key to 2captcha to get captcha ID (and parse it)
    captcha_id_pre = s.get("http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(API_KEY, site_key, url))
    captcha_id = captcha_id_pre.text.split('|')[1]
    print("Captcha ID: " + captcha_id)
    print("Solving captcha...")
    sleep(20)
    # parse gresponse from 2captcha response
    recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
    print("API response: " + recaptcha_answer)
    while 'CAPCHA_NOT_READY' in recaptcha_answer:
        sleep(5)
        recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
        print(recaptcha_answer)
        if('CAPCHA_NOT_READY' not in recaptcha_answer):
            recaptcha_answer = recaptcha_answer.split('|')[1]

    print("Success!")
    driver.execute_script("document.getElementById('g-recaptcha-response').style.display = 'block';")
    sleep(rand(2, 5))
    driver.find_element_by_id('g-recaptcha-response').send_keys(recaptcha_answer)
    # we make the payload for the post data here, use something like mitmproxy or fiddler to see what is needed
    payload = {
        'key': 'value',
        'gresponse': recaptcha_answer  # This is the response from 2captcha, which is needed for the post request to go through.
        }

    # then send the post request to the url
    response = s.post(url, payload)
    #print(response.text)
    #sleep(rand(3, 5))
    #driver.execute_script('grecaptcha.getResponse()')
    driver.execute_script("document.getElementById('g-recaptcha-response').style.display = 'none';")
    sleep(rand(3, 5))
    driver.find_element_by_xpath('/html/body/div[3]/div/div[3]/div[2]/div[2]/div/div/div/div/div[2]/form/button').click()
    #driver.execute_script('processLogin()')

driver = webdriver.Firefox(profile)
driver.get(url)
fill_log_in(driver)
solve_captcha(driver, url, API_KEY, site_key)


while 1:
    try:
        
        element = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[4]/div[1]/div[1]/div[1]/form/span[2]/span")))
        # driver.execute_script(runcode)
        sleep(2)
        script_pre=driver.find_element_by_xpath(
            '/html/body/div[4]/div[3]/p[5]/a[2]').get_attribute('href')
        print(script_pre)
        script_post=script_pre[11:]
        driver.execute_script(script_post)
        print(script_post)
        # print('click')
        sleep(4)
        driver.execute_script('document.myform.submit()')
        print('Ran Script')
        sleep(10)
    except Exception as e:
        print(e)
        sleep(10)
