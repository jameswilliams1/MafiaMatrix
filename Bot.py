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
from random import randrange, choice
import requests


def check_fail(driver):
    result = False
    if 'Login failed' in driver.page_source:
        result = True
    return result

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


email = ""
password = ""
API_KEY = '' # 2captcha API KEY
site_key = '6LeLBQwTAAAAAEjOl7RVSY-x9mxPOxSOSkkR24aY'  # site-key
url = 'https://mafiamatrix.com/'
s = requests.Session()

try:
    with open('login.txt', 'r') as f:
        email = f.readline()
        password = f.readline()
        API_KEY = f.readline()
except IOError:
    email = input('Enter email:')
    password = input('Enter password:')
    API_KEY = input('Enter 2Captcha API key:')
    with open('login.txt', 'w') as f:
        f.write(email + '\n' + password + '\n' + API_KEY)

target_job = input('Enter target job: ')

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
    #print("Captcha ID: " + captcha_id)
    print("Solving captcha, this may take a moment...")
    sleep(20)
    # parse gresponse from 2captcha response
    recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
    #print("API response: " + recaptcha_answer)
    counter = 0
    while 'CAPCHA_NOT_READY' in recaptcha_answer:
        if counter > 25:
            print('API failed to send a captcha code')
            return
        sleep(5)
        recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
        #print(recaptcha_answer)
        if('CAPCHA_NOT_READY' not in recaptcha_answer):
            recaptcha_answer = recaptcha_answer.split('|')[1]

    print("Captcha code obtained, attempting login...")
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
    sleep(rand(3, 5))
    driver.execute_script("document.getElementById('g-recaptcha-response').style.display = 'none';")
   
def hasAttribute(element, attribute): #check if certain attribute present
    result = False
    try:
        value = element.get_attribute(attribute)
        if value is not None:
            result = True
    except Exception:
        pass
    return result

def log_in_play(driver):
    print('Attempting login...')
    driver.get(url)
    #log in and solve captcha
    fill_log_in(driver)
    solve_captcha(driver, url, API_KEY, site_key)
    sleep(rand(3, 5))
    driver.find_element_by_xpath('/html/body/div[3]/div/div[3]/div[2]/div[2]/div/div/div/div/div[2]/form/button').click() #login button
    sleep(rand(8, 10))
    while "Login failed" in driver.page_source:
        print('Login failed, retrying...')
        driver.get(url)
        #log in and solve captcha
        fill_log_in(driver)
        solve_captcha(driver, url, API_KEY, site_key)
        sleep(rand(3, 5))
        driver.find_element_by_xpath('/html/body/div[3]/div/div[3]/div[2]/div[2]/div/div/div/div/div[2]/form/button').click() #login button
        sleep(rand(5, 8))


    #click play
    driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[3]/div[2]/table/tbody/tr/td[2]/div/table[5]/tbody/tr/td/div/a').click()
    print('Success!')
    sleep(rand(3, 5))
    #click income
    #driver.find_element_by_xpath('/html/body/div[4]/div[3]/p[5]/a[1]').click()
    #sleep(rand(3, 5))

def do_job(driver):
    #find and click job
    driver.get('https://mafiamatrix.com/income/earn.asp') #earns page
    sleep(rand(4, 8))
    job_list = driver.find_elements_by_tag_name('input') #get all jobs
    target_jobs_list = []
    target_job_el = ''
    target_chosen = False
    print('Finding jobs matching: %s' % target_job)
    for job in job_list:
        if(job.get_attribute('id') == 'Timeout' or job.get_attribute('type') == 'hidden'):
            continue
        else:
            target_jobs_list.append(job)
    for job in target_jobs_list:
        if target_job.lower() in job.get_attribute('id').lower():
            target_job_el = job
            target_chosen = True
            break
    if not target_chosen:
        target_job_el = choice(target_jobs_list)
        print('Could not find jobs matching %s, choosing a random job' % target_job)
    target_job_el.click()
    sleep(rand(2, 4))
    driver.find_element_by_xpath('/html/body/div[4]/div[4]/div[1]/div[2]/form/p/input').click()



def check_earn_options(driver): #check if pop up blocks earn
    sleep(rand(8, 12))
    if (EC.presence_of_element_located((By.XPATH, '//*[@id="earns_options"]'))):
        print('Solving job test...')
        earn_options = driver.find_elements_by_tag_name('input')
        for earn_option in earn_options:
            try:
                earn_id = earn_option.get_attribute('id')
                earn_type = earn_option.get_attribute('type')
                if(earn_id == 'Timeout' or earn_type == 'hidden'):
                    continue
                elif earn_type == 'radio':
                    earn_option.click()
                    sleep(rand(2, 3))
                    driver.find_element_by_xpath('/html/body/div[4]/div[4]/div[1]/div[2]/form/p/input').click()
                    print('Success!')
                    break
            except:
                pass

#profile = get_profile_path("default") #sets bot to users defualt firefox profile
#profile = webdriver.FirefoxProfile()
driver = webdriver.Firefox()
log_in_play(driver)


do_job(driver)
sleep(rand(5, 8))
check_earn_options(driver)
sleep(rand(5, 8))


while 1:
    try:
        sleep(rand(2, 5))
        #check for captcha
        if("Click the button to confirm you're not a bot or a script" in driver.page_source):
            print("Random captcha test: " + driver.current_url)
            #sleep(rand(2, 5))
            #solve_captcha(driver, url, API_KEY, site_key)
            #sleep(rand(4, 8))
            #driver.find_element_by_xpath('/html/body/div[4]/div[4]/div[2]/form/div[2]/p[2]/input').click()
            #sleep(rand(5, 10))
            #do_job(driver)
            log_in_play(driver)
            do_job(driver)
            sleep(rand(5, 8))
            check_earn_options(driver)
            sleep(rand(5, 8))


        #look for "ready"
        element = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[4]/div[1]/div[1]/div[1]/form/span[2]/span")))
        sleep(rand(2, 6))
        script_pre=driver.find_element_by_xpath(
            '/html/body/div[4]/div[3]/p[5]/a[2]').get_attribute('href')
        script_post=script_pre[11:]
        driver.execute_script(script_post)
        sleep(4)
        driver.execute_script('document.myform.submit()')
        print("Completed job")
        sleep(10)
        check_earn_options(driver)
    except Exception as e:
        #print(e)
        sleep(10)
