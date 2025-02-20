import os
import sys
import time
import traceback
from random import random, randint
import numpy as np
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import InvalidSessionIdException, NoSuchElementException, NoSuchWindowException, StaleElementReferenceException
from parse_arguments import parse_args

class PoshmarkHelpers:
    @staticmethod
    def add_jitter(value):
        sigma = 1
        value = int(value)
        return randint(value - sigma, value + sigma)

    @staticmethod
    def sleep(value):
        time.sleep(PoshmarkHelpers.add_jitter(value))


class PoshmarkConstants:
    '''
    Constants used for driving the Poshmark site for logging in,
    getting and sharing closet items
    '''
    class URLs:
        login = "https://poshmark.ca/login"

        @staticmethod
        def get_user_closet(username):
            return f'https://poshmark.ca/closet/{username}'

        @staticmethod
        def get_user_available_listings(username):
            return PoshmarkConstants.URLs.get_user_closet(username) + \
                   '?availability=available'

        @staticmethod
        def get_user_following(username):
            return f'https://poshmark.ca/user/{username}/following'

    class Login:
        username_element = "login_form[username_email]"
        password_element = "login_form[password]"

    class Closet:
        share_class = "//div[@class='d--fl ai--c social-action-bar__action social-action-bar__share']"
        share_icon_class = 'share-gray-large'

    class Actions:
        click = "arguments[0].click();"
        scroll = "window.scrollTo(0, document.body.scrollHeight);"
        get_height = "return document.documentElement.scrollHeight"

    class Share:
        internal_share_class = "//a[@class='internal-share__link']"

    class Credentials:
        credentials_path = './credentials.py'

    class Following:
        follower_class = "//p[@class='follow__action__follower caption ellipses tc--lg']"

    class Captcha:
        captcha_div = "//div[@class='d--fl  jc--c g-recaptcha-con']"


class PoshmarkDriver:
    '''
    Class for running the webdriver to navigate Poshmark
    '''
    def __init__(
            self,
            poshmark_username,
            loop_delay,
            pages,
            num_items):

        # Poshmark username used to login
        self.poshmark_username = poshmark_username

        # Amount of time to wait between running share closeet loop
        self.loop_delay = loop_delay

        # Number of pages to scroll for each closet
        self.pages = pages

        # Number of items to share for each closet
        self.num_items = num_items

        # Webdriver.  Gets instantiated, then removed during run_driver_loop
        self.driver = None

    @staticmethod
    def get_driver():
        # Driver expected to be installed at the following location.
        # If this is incorrect for your system, you can either:
        # 1. Edit to the location of the webdriver on your system, or
        # 2. Add the webdriver location in your system path and remove
        #    the driver_location argument from the webdriver.Chrome() call
        driver_location = '/Applications/chromedriver-mac-x64/chromedriver'
        driver = webdriver.Chrome(driver_location)
        driver.implicitly_wait(0)
        return driver

    @staticmethod
    def validate_credentials():
        if not os.path.isfile(PoshmarkConstants.Credentials.credentials_path):
            print(f'Credentials path not found at '
                  f'{PoshmarkConstants.Credentials.credentials_path}.\n')
            sys.exit()
        else:
            import credentials
        return credentials

    @staticmethod
    def get_login_credentials():
        credentials = PoshmarkDriver.validate_credentials()
        return credentials.poshmark_username, credentials.poshmark_password

    def login(self, poshmark_password):
        # Navigate to Poshmark login page
        self.driver.get(PoshmarkConstants.URLs.login)
        time.sleep(3)

        # Get the usernanme and password fields, and populate with the
        # credentials
        print(f'\nLogging in to Poshmark as username {self.poshmark_username}\n')
        username = self.driver.find_element_by_name(PoshmarkConstants.Login.username_element)
        username.send_keys(self.poshmark_username)
        password = self.driver.find_element_by_name(PoshmarkConstants.Login.password_element)
        password.send_keys(poshmark_password)
        password.send_keys(Keys.RETURN)

        # Wait 5 seconds for the page to load after logging in
        time.sleep(5)

    def go_to_seller_closet(self, username):
        seller_closet = PoshmarkConstants.URLs.get_user_available_listings(username)
        self.driver.get(seller_closet)

    def scroll_page(self, pages):
        scroll = 0
        screen_heights = [0]
        for i in range(pages):
            scroll +=1
            self.driver.execute_script(PoshmarkConstants.Actions.scroll)
            height = self.driver.execute_script(PoshmarkConstants.Actions.get_height)
            last_height = screen_heights[-1:][0]

            if height == last_height:
                return
            else:
                screen_heights.append(height)
                time.sleep(1)

    def get_closet_share_icons(self):
        items = self.driver.find_elements_by_xpath(PoshmarkConstants.Closet.share_class)
        share_icons = [i.find_element_by_class_name(PoshmarkConstants.Closet.share_icon_class) for i in items]
        return share_icons

    def click_share_to_followers(self, share_icon):
        # Click the share icon, then wait 2 seconds
        self.driver.execute_script(PoshmarkConstants.Actions.click, share_icon)
        time.sleep(2)

        # Find the element to share to followers
        share_followers = self.driver.find_element_by_xpath(PoshmarkConstants.Share.internal_share_class)

        # Click share to followers, then wait 2 seconds
        self.driver.execute_script(PoshmarkConstants.Actions.click, share_followers)
        time.sleep(2)

        # Check to see if there is a captcha
        try:
            captcha = self.driver.find_element_by_xpath(PoshmarkConstants.Captcha.captcha_div)
        except NoSuchElementException:
            return

        out = input(f'Encountered captcha.  Please hit enter once you have completed it.\n\n')
        self.click_share_to_followers(share_icon)

    def share_listings(self, seller):
        num_items = PoshmarkHelpers.add_jitter(self.num_items)
        self.go_to_seller_closet(seller)
        self.scroll_page(self.pages)
        share_icons = self.get_closet_share_icons()
        num_share_icons = len(share_icons)
        if num_share_icons < num_items:
            print(f'        {seller} closet has less than {num_items} available items; moving on.\n')
            return

        # To share the oldest closet items first, reverse the order of the list
        share_icons.reverse()

        # Select a random number of items to share from the closet (if num_items is > 0)
        if self.num_items != 0:
            share_icons = np.random.choice(share_icons, num_items, replace=False).tolist()
        print(f'        Sharing {num_items if self.num_items != 0 else num_share_icons} of {num_share_icons} '
              f'listings')

        # Share the closet listings
        for item in tqdm(share_icons, total=len(share_icons), desc='        '):
            try:
                self.click_share_to_followers(item)
            except InvalidSessionIdException as exc:
                print(f'Invalid Session Id: {exc}')
                traceback.print_exc(file=sys.stdout)
            except NoSuchElementException as exc:
                print(f'No Such Element: {exc}')
                traceback.print_exc(file=sys.stdout)
            except StaleElementReferenceException as exc:
                print(f'Stale Element: {exc}')
                traceback.print_exc(file=sys.stdout)
            except NoSuchWindowException as exc:
                print(f'No Such Window: {exc}')
                traceback.print_exc(file=sys.stdout)
                break
        print('\n')

    def run_driver(self, poshmark_password, seller=None, num_following=0):
        self.driver = self.get_driver()
        self.login(poshmark_password)
        time.sleep(4)
        sellers = [seller]
        if seller is None:
            sellers = self.get_following_usernames(num_following)
        for i, seller in enumerate(sellers):
            print(f'    {seller} ({i} of {len(sellers)})')
            try:
                self.share_listings(seller)
            except InvalidSessionIdException as exc:
                print(f'Invalid Session Id 2: {exc}')
                traceback.print_exc(file=sys.stdout)
            except NoSuchWindowException as exc:
                # if this exception is encountered, the window has been closed.
                print(f'No Such Window: {exc}')
                traceback.print_exc(file=sys.stdout)
                self.driver = None
                break

        time.sleep(3)
        if self.driver is not None:
            self.driver.close()
        self.driver = None

    def get_following_usernames(self, num_following):
        url = PoshmarkConstants.URLs.get_user_following(self.poshmark_username)
        self.driver.get(url)
        time.sleep(3)
        self.scroll_page(8)
        time.sleep(3)
        follower_elements = self.driver.find_elements_by_xpath(PoshmarkConstants.Following.follower_class)
        followers = [f.text.lstrip('@') for f in follower_elements]
        if num_following == 0 or num_following > len(followers):
            print(f'Found {len(followers)} followers.  Sharing closet for all.\m')
        else:
            print(f'Found {len(followers)} followers.  Of these, selecting {num_following} closets to share.\n')
            followers = np.random.choice(followers, num_following, replace=False).tolist()
        return followers

    def run_loop_share(self, poshmark_password, seller=None, num_following=0):
        while True:
            random_loop_time = PoshmarkHelpers.add_jitter(self.loop_delay)

            self.run_driver(
                poshmark_password,
                seller=seller,
                num_following=num_following
            )

            current_time = time.strftime("%I:%M%p on %b %d, %Y")
            print(f'Will share again in {int(random_loop_time / 60)} minutes.\n'
                  f'Current time: {current_time}\n\n')
            PoshmarkHelpers.sleep(random_loop_time)

    def run_loop_share_for_sellers(self, poshmark_password, seller):
        self.run_loop_share(poshmark_password, seller=seller)

    def run_loop_share_following_users(self, poshmark_password, num_following):
        self.run_loop_share(poshmark_password, num_following=num_following)


def main():
    args = parse_args()

    poshmark_username, poshmark_password = PoshmarkDriver.get_login_credentials()

    # if args.self is selected, set the value of args.num_items to 0 (use all)
    num_items = 0 if args.self else args.num_items

    poshmark_driver = PoshmarkDriver(poshmark_username, args.time, args.pages, num_items)

    if args.self or args.account:
        '''
        If args.self is selected, share your own closet.
        If args.account is specified, use the seller value set using --account
        '''
        if args.self:
            seller = poshmark_username
        else:
            seller = args.account
        poshmark_driver.run_loop_share_for_sellers(
            poshmark_password,
            seller=seller)
    else:
        '''
        Otherwise, default is to share items from the closets of the sellers you follow
        '''
        poshmark_driver.run_loop_share_following_users(
            poshmark_password,
            args.following)



if __name__ == '__main__':
    main()
