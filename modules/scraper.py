import re
import time

from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Scraper(object):
    """Able to start up a browser, to authenticate to Instagram and get
    followers and people following a specific user."""

    def __init__(self, target):
        self.target = target
        self.driver = webdriver.Chrome("drivers/chromedriver")
        self.actions = ActionChains(self.driver)
        self.wait = WebDriverWait(self.driver, 5)

    def close(self):
        """Close the browser."""

        self.driver.close()

    def authenticate(self, username, password, cookies_list):
        """Log in to Instagram with the provided credentials."""

        print('\nLogging in…')
        self.driver.get('https://www.instagram.com')
        print("Get instagram.com...")
        for cookie in cookies_list:
            self.driver.add_cookie(cookie)
        self.driver.refresh()
        print("Adding cookies...")

        # Check if suspicious activity window is visible
        try:
            sus_elem = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[role='button'][aria-label='Dismiss']")))
            sus_elem = self.driver.find_element(
                "css selector", "div[role='button'][aria-label='Dismiss']")
        except:
            sus_elem = None
            print("No Bot Warning found.")

        if sus_elem is not None:
            sus_elem.click()

        try:
            # notification_elem = self.driver.find_element("css selector", "button")
            notification_elem = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Not Now']")))
            notification_elem = self.driver.find_element(
                By.XPATH, "//button[text()='Not Now']")
        except:
            notification_elem = None
            print("No Notification Popup found.")

        if notification_elem is not None:
            notification_elem.click()

    def get_users(self, group, verbose=False):
        """Return a list of links to the users profiles found."""

        self._open_dialog(self._get_link(group), group)

        print('\nGetting {} users…{}'.format(
            self.expected_number,
            '\n' if verbose else ''
        ))

        links = []
        updated_list = self._get_updated_user_list()
        retry = 2
        
        # Wait for the first user element to be present
        self.wait.until(EC.presence_of_element_located((By.XPATH, './/a')))

        # While there are more users scroll and save the results
        while retry > 0:
            try:
                # print(self.scroll_container.text)
                self._scroll(self.scroll_container)
                print("scrolled")
                retry = 2
            except Exception as e:
                retry -= 1
                print(f"An exception occurred: {e}")

            time.sleep(2)
            updated_list = self._get_updated_user_list()
            print(updated_list[0].text)

        print('100% Complete')
        return links

    def _open_dialog(self, link, group):
        """Open a specific dialog and identify the div containing the users
        list."""

        link.click()
        a_elem = self.driver.find_element(
            By.CSS_SELECTOR, f"a[href='/{self.target}/{group}/']")
        number_elem = a_elem.find_element(By.CSS_SELECTOR, "span._ac2a")
        self.expected_number = number_elem.get_attribute("title")

        # Wait for the dialog to be present
        dialog_xpath = '//div[@role="dialog"]'
        dialog_locator = (By.XPATH, dialog_xpath)
        self.wait.until(EC.presence_of_element_located(dialog_locator))
        time.sleep(1)
        self.users_list_container = self.driver.find_element(*dialog_locator)
        self.scroll_container = self.users_list_container.find_element(
            By.CSS_SELECTOR, "div._aano")
        print(f"Scroll container found: {self.scroll_container.text}")
        
        # Wait for the first user element to be present
        self.wait.until(EC.presence_of_element_located((By.XPATH, './/a')))

    def _get_link(self, group):
        """Return the element linking to the users list dialog."""

        print('\nNavigating to %s profile…' % self.target)
        self.driver.get('https://www.instagram.com/%s/' % self.target)
        try:
            return self.wait.until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, group))
            )
        except Exception as e:
            self._get_link(group)
            print(f"An exception occurred: {e}")

    def _get_updated_user_list(self):
        """Return all the list items included in the users list."""
        time.sleep(3)
        return self.users_list_container.find_elements(By.XPATH, './/a')
        
    def _scroll(self, element, pixels=1000):
        """Scroll a specific element by a certain amount of pixels."""
    
        self.driver.execute_script(f"arguments[0].scrollBy(0, {pixels});", element)
        time.sleep(3)
