"""A class of main.py"""
import re
import sys
import time
from collections import deque
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup

from base_url import base_url


class Scraper:
    email_dict = {}
    url_counter = {}
    queue_counter = {}
    processed_urls = []
    url_cap = 1500

    def __init__(self, url):
        # Check if url is a string and over-write it as a list if it is
        if type(url) == str:
            url = [url]

        self.new_urls = deque(url)
        self.response = None
        self.current_url = None
        self.poss_link = None

    def get_new_urls(self):
        return self.new_urls

    def get_current_url(self):
        return self.current_url

    def get_current_base_url(self):
        return base_url(self.get_current_url())

    def get_next_url(self):
        # get the next url in deque
        return self.new_urls[-1]

    def set_new_urls(self, url_list):
        # update new_urls with a list of new urls
        if type(url_list) == list:
            self.new_urls = deque(url_list)
            return print(f'new_urls set to {self.new_urls}')
        if type(url_list) == str:
            self.new_urls = deque([url_list])
            return print(f'new_urls set to {self.new_urls}')

    def set_current_url(self):
        # get the url from new_urls, move url to processed_urls, return url
        url = self.new_urls.popleft()
        self.processed_urls.append(url)
        # print(f'{url} added to Processed URLS:{self.processed_urls}')
        self.current_url = url

    def set_response(self):
        # Get current url and set response to the HTML received
        url = self.get_current_url()
        try:
            response = requests.get(url, timeout=10).text
            self.response = response
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema,
                requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,
                requests.exceptions.Timeout, requests.exceptions.TooManyRedirects) as e:
            print(f'Link Error: {e}')

    def set_email_dict_default(self):
        # adds an entry into the email dict, 'base_url': []
        self.email_dict.setdefault(self.get_current_base_url(), [])

    def email_from_charcode(self):
        # TODO: SOLVE EMAIL FROM CHARCODE!!!
        pass

    def get_email_from_response(self):
        # Uses the email regex to extract the emails from response and adds the new emails to list if it isn't already
        # in the list

        # get new emails from response html
        new_emails = list(set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+",
                                         self.response, re.I)))

        # check if any of the emails in new_emails are in the email_dict, remove email if so
        # if new_emails:
        #     new_emails = [i.lower() for i in new_emails]
        #     try:
        #         captured_url_emails = self.email_dict[self.get_current_base_url()]
        #         for email in new_emails:
        #             if email in captured_url_emails:
        #                 new_emails.remove(email)
        #     except KeyError:
        #         for email_list in self.email_dict.values():
        #             for e_mail in email_list:
        #                 if e_mail in new_emails:
        #                     new_emails.remove(e_mail)
        # TODO: TEST REMOVE REPEATING EMAILS CODE BLOCK
        if new_emails:
            print(new_emails)
            new_emails = [i.lower() for i in new_emails]
            try:
                captured_url_emails = self.email_dict[self.get_current_base_url()]
            except KeyError:
                self.set_email_dict_default()
            captured_url_emails = self.email_dict[self.get_current_base_url()]
            for email in new_emails:
                if email in captured_url_emails:
                    new_emails.remove(email)

            # Add new emails to the correct dictionary or add an entry if there isn't one
            try:
                email_list = self.email_dict[self.get_current_base_url()]
            except KeyError:
                self.email_dict.setdefault(self.get_current_base_url(), new_emails)
                email_list = self.email_dict[self.get_current_base_url()]
            # Add the email to email_dict
            for email in new_emails:
                print(f'Email Found: {self.get_current_base_url()} on {self.current_url}')
                email_list.append(email)
        else:
            print('No Email Found') # Test print line

    def set_default_url_counter(self):
        self.url_counter.setdefault(self.get_current_base_url(), 0)

    def set_default_queue_counter(self):
        # set queue counter to default, 'url_base': 1
        self.queue_counter.setdefault(self.get_current_base_url(), 1)

    def add_to_new_urls(self, url):
        # Add another url to new_urls
        self.new_urls.append(url)

    def add_url_counter(self):
        # increment the url counter in url_counter by 1 if it exists, set default if it doesn't and increment
        if self.url_counter.get(self.get_current_base_url()):
            self.url_counter[self.get_current_base_url()] += 1
        else:
            self.set_default_url_counter()
            self.url_counter[self.get_current_base_url()] += 1

    def add_queue_counter(self):
        # increment url base in queue counter by one
        try:
            self.queue_counter[self.get_current_base_url()] += 1
        except KeyError:
            print(f'KeyError: Create a default entry for {self.get_current_base_url()} with .set_default_queue_counter')

    def is_url_capped(self):
        # Return True if the url is capped, False if it isn't
        if self.url_counter.get((self.get_current_base_url())):
            if self.url_counter.get(self.get_current_base_url()) >= self.url_cap:
                return True
            return False
        self.set_default_url_counter()
        return False

    def is_poss_link_a_link(self):
        # TODO: SELF.POSS_LINK ARE LINKS COLLECTED FROM THE BEAUTIFUL SOUP FIND LINKS LOOPS
        # TODO: UNFINISHED!
        exclude_ext = ['image', 'pdf', 'jpg', 'png', 'gif', 'xlsx', 'spx',
                       'mp3', 'csv', 'wma', 'provider', 'specialtie', 'pptx',
                       'asp', 'mp4', 'download', 'javascript', 'tel:', 'pdf',
                       'specialty']

        # check link for criteria
        for extension in exclude_ext:
            # skips over links with the following keywords from exclude_ext
            if extension in self.poss_link:
                print(f'Extension: {extension} in {self.poss_link}')
                return False
        if self.poss_link in self.processed_urls:
            # link is already in the processed urls
            print(f'Link: {self.poss_link} in processed urls.')
            return False
        elif self.poss_link in self.new_urls:
            # link is already in new urls
            print(f'Link: {self.poss_link} in new urls')
            return False
        elif self.poss_link.startswith('mailto:'):
            # link is a mailto: link, extract email from mailto:, and add it to the email list if not already in there
            email_from_link = self.poss_link[7:]
            try:
                # Check if base_url key exists, if it doesn't create it
                email_list = self.email_dict.get(self.get_current_base_url())
            except KeyError:
                # Create key:value default entry
                self.set_email_dict_default()
                email_list = self.email_dict.get(self.get_current_base_url())
            # Check if email from link is in the email_list, add it if not
            if email_from_link not in email_list:
                email_list.append(email_from_link)
            return False
        elif self.get_current_base_url() not in self.poss_link:
            # Base url is not in the link, ex. 'http://instagram.com/company_profile
            print(f'Link: {self.poss_link} doesnt have url base {self.get_current_base_url()}')
            return False
        else:
            return True

    def get_new_urls_from_html(self):
        # TODO: TEST ME!
        # TODO: UNFINISHED!
        # get new url links from html and add them to the new urls deque()
        soup = BeautifulSoup(self.response, features='html.parser')
        self.set_default_queue_counter()

        # Go through every link in html and add it to list
        for anchor in soup.find_all('a'):

            # check if base url is capped
            if self.queue_counter.get(self.get_current_base_url()) >= self.url_cap:
                print(f'Queue Capped: {self.get_current_base_url()}: {self.queue_counter[self.get_current_base_url()]}')
                break

            try:
                if 'href' in anchor.attrs or anchor.attrs['href'].find('mailto') == -1:
                    self.poss_link = anchor.attrs['href']
                else:
                    print(f'LINE 161: Link: {anchor} didnt have href, WARNING', file=sys.stderr)
            except KeyError:
                print(f'KeyError: Anchor: {anchor}, Link: {self.get_current_url()}', file=sys.stderr)
                continue

            # resolve relative links method placeholder
            if self.poss_link.startswith('/'):
                self.poss_link = self.get_current_base_url() + self.poss_link

            # check link criteria, .is_link, placeholder
            if self.is_poss_link_a_link():
                self.add_to_new_urls(self.poss_link)
                print(f'New URL Added: {self.poss_link}')
                self.add_queue_counter()



