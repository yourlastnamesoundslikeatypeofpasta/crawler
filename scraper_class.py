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
        self.new_urls = deque([url])

    def get_url_base(self):
        # get the url base address
        url = self.new_urls[0]
        return base_url(url)

    def get_next_url(self):
        # get the next url in deque and move the url from new_urls to
        url = self.new_urls[-1]
        self.add_url_to_processed()
        return url

    def add_url_to_processed(self):
        # add the url to the processed urls list
        url = self.new_urls.popleft()
        self.processed_urls.append(url)
        print(f'{url} added to Processed URLS:{self.processed_urls}')

    def add_url_counter(self):
        # increment the url counter in url_counter by 1
        self.url_counter.setdefault(self.get_url_base(), 0)
        self.url_counter[self.get_url_base()] += 1

    def is_url_capped(self):
        # Return True if the url is capped, False if it isn't
        if self.url_counter[self.get_url_base()] >= self.url_cap:
            return True
        return False

    def get_url_html(self, url):
        print(f'Processing {self.new_urls}')


url_1 = Scraper('google.com')
# print(url_1.url_counter)
# for i in range(1500):
#     url_1.add_url_counter()
# print(url_1.url_counter)
# print(url_1.is_url_capped())
print(url_1.get_next_url())