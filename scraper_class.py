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
        self.url = deque([url])

    def get_url_base(self):

        # get the url base address
        url = self.url[0]
        return base_url(url)

    def get_next_url(self):

        # get the next url in deque
        url = self.url[-1]
        return url

    def process_url(self):
        # add the url to the processed urls list
        self.processed_urls.append(self.url)
        print(f'{self.url} added to Processed URLS:{self.processed_urls}')

    def get_parts(self):
        url = self.url
        url_base = self.get_url_base()
        parts = urlsplit(url_base)

        if parts.scheme != 'mailto' and parts.scheme != '#':
            if'/' in parts.path:
                path = self.url[:self.url.rfind]


url_1 = Scraper('google.com')
print(url_1.get_url_base())
print(url_1.get_next_url())
