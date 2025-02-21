import os
import sys
import time
import traceback
import numpy as np
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import InvalidSessionIdException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import StaleElementReferenceException

from src.poshmark_helpers import PoshmarkHelpers
from src.poshmark_constants import PoshmarkConstants



class PoshmarkDriver:
    '''
    Class for running the webdriver to navigate Poshmark
    '''
    def __init__(self, poshmark_username):

        # Poshmark username used to login
        self.poshmark_username = poshmark_username

        # By default, paginate through the first 3 pages of the user's own closet
        self.pages = 3

        # Webdriver
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
            raise Exception(f'Credentials path not found at '
                  f'{PoshmarkConstants.Credentials.credentials_path}.\n')
        else:
            import credentials
        return credentials

    @staticmethod
    def get_login_credentials():
        credentials = PoshmarkDriver.validate_credentials()
        return credentials.poshmark_username, credentials.poshmark_password

    def login(self, poshmark_password):
        # create driver
        self.driver = self.get_driver()
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
            time.sleep(2)

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
            # Try finding the captcha element
            self.driver.find_element_by_xpath(PoshmarkConstants.Captcha.captcha_div)
        except NoSuchElementException:
            # If captcha element not found, there is no captcha -> move on
            return

        # Waits for user input once captcha is completed
        out = input(f'Encountered captcha.  Please hit enter once you have completed it.\n\n')

        # Try again once captcha is cleared
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

    def run_driver(self, sellers):
        for i, seller in enumerate(sellers):
            print(f'    {seller} ({i+1} of {len(sellers)})')
            try:
                self.share_listings(seller)
            except InvalidSessionIdException as exc:
                print(f'Invalid Session Id: {exc}')
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

    def get_total_count(self, xpath):
        try:
            total_following_element = self.driver.find_elements_by_xpath(xpath)
            print(f'got total_following_element: {total_following_element}')
            return int(total_following_element[0].text)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            raise Exception(f'Error finding total number of sellers following')



