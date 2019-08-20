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
    exclude_ext = ['image', 'pdf', 'jpg', 'png', 'gif', 'xlsx', 'spx',
                   'mp3', 'csv', 'wma', 'provider', 'specialtie', 'pptx',
                   'asp', 'mp4', 'download', 'javascript', 'tel:', 'pdf',
                   'specialty']

    def __init__(self, url):
        # Check if url is a string and over-write it as a list if it is
        if type(url) == str: # TODO: TEST ME!
            url = [url]

        self.new_urls = deque(url)
        self.response = None
        self.current_url = None

    def get_new_urls(self):
        # TODO: TEST ME!
        return self.new_urls

    def get_current_url(self):
        # TODO: TEST ME!
        return self.current_url

    def get_current_base_url(self):
        # TODO: TEST ME!
        return base_url(self.get_current_url())

    def get_next_url(self):
        # TODO: TEST ME!
        # get the next url in deque
        return self.new_urls[-1]

    def set_new_urls(self):
        # TODO: TEST ME!
        new_urls = input("Please enter the name of the website you'd like to scrape\n: ")
        self.new_urls = [new_urls]

    def set_current_url(self):
        # TODO: TEST ME!
        # get the url from new_urls, move url to processed_urls, return url
        url = base_url(self.new_urls.popleft())
        self.processed_urls.append(url)
        print(f'{url} added to Processed URLS:{self.processed_urls}')
        self.current_url = url

    def set_response(self):
        # TODO: TEST ME!
        # Get current url and set response to the HTML received
        url = self.get_current_url()
        try:
            response = requests.get(url, timeout=10).text
            self.response = response
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema,
                requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,
                requests.exceptions.Timeout, requests.exceptions.TooManyRedirects) as e:
            print(f'Link Error: {e}')

    def set_email_dict_from_response(self):
        # TODO: TEST ME!
        # Uses the email regex to extract the emails from response and adds the new emails to list if it isn't already
        # in the list

        # get new emails from response html
        new_emails = list(set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+",
                                         self.response, re.I)))

        # check if any of the emails in new_emails are in the email_dict, remove email if so
        if new_emails:
            new_emails = [i.lower() for i in new_emails]
            try:
                captured_url_emails = self.email_dict.get(self.get_current_base_url())
                if new_emails:
                    for email in new_emails:
                        if email in captured_url_emails:
                            new_emails.remove(email)
            except KeyError:
                for email_list in self.email_dict.values():
                    for e_mail in email_list:
                        if e_mail in new_emails:
                            new_emails.remove(e_mail)

            # Add new emails to the correct dictionary or add an entry if there isn't one
            try:
                email_list = self.email_dict.get(self.get_current_base_url())
                for email in new_emails:
                    email_list.append(email)
            except KeyError:
                self.email_dict.setdefault(self.get_current_base_url(), new_emails)

    def add_url_counter(self):
        # TODO: TEST ME!
        # FIXME: Turn me into a class method
        # increment the url counter in url_counter by 1
        self.url_counter.setdefault(self.get_current_base_url()), 0)
        self.url_counter[self.get_current_base_url()] += 1

    def is_url_capped(self):
        # TODO: TEST ME!
        # FIXME: Turn me into a class method
        # Return True if the url is capped, False if it isn't
        if self.url_counter.get(self.get_current_base_url()) >= self.url_cap:
            return True
        return False

url_1 = Scraper('google.com')
# print(url_1.url_counter)
# for i in range(1500):
#     url_1.add_url_counter()
# print(url_1.url_counter)
# print(url_1.is_url_capped())
# print(url_1.get_next_url())
html = url_1.set_response_html()

print(url_1.response)
