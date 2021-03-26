import bs4
import sys
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException, WebDriverException
from twilio.rest import Client
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from twilio.base.exceptions import TwilioRestException
from multiprocessing import Process

# Amazon credentials
username = 'XXXXXXX'
password = 'XXXXXXX'

# Amazon URL´s

limit = 800
urls = ['https://www.amazon.com/dp/B08L8KC1J7',
        'https://www.amazon.com/dp/B08KWLMZV4']

# Twilio configuration
toNumber = 'your_phonenumber'
fromNumber = 'twilio_phonenumber'
accountSid = 'ssid'
authToken = 'authtoken'
client = Client(accountSid, authToken)


def timeSleep(x, driver):
    for i in range(x, -1, -1):
        sys.stdout.write('\r')
        sys.stdout.write(f'{i} seconds')
        sys.stdout.flush()
        time.sleep(1)
    try:
        driver.refresh()
    except WebDriverException:
        pass
    sys.stdout.write('\r')
    sys.stdout.write(f' PID: {driver.capabilities["moz:processID"]} => Page refreshed\n')
    sys.stdout.flush()


def createDriver():
    """Creating driver."""
    options = Options()
    # Change To False if you want to see Firefox Browser Again.
    options.headless = False
    profile = webdriver.FirefoxProfile(
        r'C:\Users\Username\AppData\Roaming\Mozilla\Firefox\Profiles\o5rqr2sr.default')
    driver = webdriver.Firefox(
        profile, options=options, executable_path=GeckoDriverManager().install())
    return driver


def driverWait(driver, findType, selector):
    """Driver Wait Settings."""
    while True:
        if findType == 'css':
            try:
                driver.find_element_by_css_selector(selector).click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(0.2)
            except ElementClickInterceptedException:
                print("Failed to click, will try again after 1 second")
                time.sleep(1)

        elif findType == 'name':
            try:
                driver.find_element_by_name(selector).click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(0.2)
            except ElementClickInterceptedException:
                print("Failed to click, will try again after 1 second")
                time.sleep(1)

        elif findType == 'text':
            try:
                driver.find_element_by_xpath(
                    "//input[@class='" + selector + "']").click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(0.2)
            except ElementClickInterceptedException:
                print("Failed to click, will try again after 1 second")
                time.sleep(1)


def loginAttempt(driver, url):
    """Attempting to login Amazon Account."""
    driver.get('https://www.amazon.com/gp/sign-in.html')
    try:
        usernameField = driver.find_element_by_css_selector('#ap_email')
        usernameField.send_keys(username)
        driverWait(driver, 'css', '#continue')
        passwordField = driver.find_element_by_css_selector('#ap_password')
        passwordField.send_keys(password)
        driverWait(driver, 'css', '#signInSubmit')
        for i in range(1, -1, -1):
            sys.stdout.write('\r')
            sys.stdout.write(
                'Redirecting to store page in {:2d} seconds'.format(i))
            sys.stdout.flush()
            time.sleep(1)
    except NoSuchElementException:
        pass
     # redirect to
    driver.get(url)


def findingCards(driver, url):
    """Scanning all cards."""
    while True:
        html = driver.page_source
        soup = bs4.BeautifulSoup(html, 'html.parser')

        try:

            # get price
            price_string = soup.find('span', {'id': 'priceblock_ourprice'}).get_text()
            price = dollar_dec = float(price_string[1:])
            price = dollar_dec = float(price_string[1:])

            if price > limit:
                print("\a \n Card value is greater than expected "+price_string)
                raise Exception("Card value is greater than expected "+price_string)

            findAllCards = soup.find_all(
                'span', {'id': 'submit.buy-now-announce'})
            for card in findAllCards:
                if 'Buy Now' in card.get_text():
                    ordered = False
                    print('\nCard Available!')
                    driverWait(driver, 'css', '#buy-now-button')
                    print('\nBuy now button clicked!')

                    time.sleep(1.5)

                    failed = False
                    tries = 0
                    while tries < 2:
                        try:
                            driver.switch_to.frame(driver.find_element_by_xpath(
                                '//*[@id="turbo-checkout-iframe"]'))
                            driver.find_element_by_xpath(
                                '//*[@id="turbo-checkout-pyo-button"]').click()
                            print('Buy Now Order Placed!!')
                            driver.switch_to.default_content()
                            ordered = True
                            print('\a')
                            break
                        except (NoSuchElementException, TimeoutException):
                            failed = True
                            print('\nFailed to locate Turbo Checkout Button\n')
                            tries += 1
                            time.sleep(1)
                            if tries == 2:
                                print('\nTurbo Checkout Button not present!\n')

                    tries = 0

                    while tries < 2 and not ordered:
                        try:
                            driver.find_element_by_name('placeYourOrder1').click()
                            print('\nPlace your Order button clicked!')
                            ordered = True
                            print('\a')
                            break
                        except (NoSuchElementException, TimeoutException):
                            print('\nfailed to locate Place Order Button')
                            time.sleep(1)
                            tries += 1

                    tries = 0

                    while ordered:
                        try:
                            driver.find_element_by_name('forcePlaceOrder').click()
                            print('\nOrder Placed!!')
                            ordered = True
                            print('\a')
                        except (NoSuchElementException, TimeoutException):
                            failed = True
                            print('\nfailed to locate ForcePlaceOrder element')
                            time.sleep(1)
                            tries +=1
                            if tries >=2 : break

                    try:
                        client.messages.create(
                            to=toNumber, from_=fromNumber, body='ORDER PLACED!')
                    except (NameError, TwilioRestException):
                        pass

                    if ordered:
                        for i in range(3):
                            print('\a')
                            time.sleep(1)

                    driver.get(url)
                    findingCards(driver, url)

        except:
            pass
        timeSleep(5, driver)


def checking_process(position):
    driver = createDriver()
    loginAttempt(driver, urls[position])
    findingCards(driver, urls[position])



if __name__ == '__main__':

    processes = []

    for url in range(len(urls)):
        process = Process(target=checking_process, args=[url])
        process.start()
