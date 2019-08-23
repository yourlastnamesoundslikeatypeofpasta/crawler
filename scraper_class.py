"""A class version of main.py"""
import re
import sys
import time
from collections import deque
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup

from base_url import base_url


class Scraper:
    # Dictionary that stores emails {'base_url': ['email_0', 'email_1']}
    email_dict = {}

    # Dictionary that stores the number of times a base_url has been processed {'base_url': 21}
    url_counter = {}

    # Dictionary that stores the number of links added to from scraped links {'base_url': 45}
    queue_counter = {}

    # List of urls that have been processed
    processed_urls = []

    # Max number of links to add to the new_urls list
    url_cap = 1500

    def __init__(self, url):
        # Check if url is a string and over-write it as a list if it is
        if type(url) == str:
            url = [url]

        self.new_urls = deque(url)
        self.response = None
        self.current_url = None
        self.poss_link = None

        # Create a default dictionary entry for each website in email_dict, url_counter, queue_counter
        # TODO: Remove all try: except: statements from methods that look for a dictionary value and then create it,
        #  if not found.
        for link in url:
            self.email_dict.setdefault(base_url(link), [])
            self.url_counter.setdefault(base_url(link), 0)
            self.queue_counter.setdefault(base_url(link), 0)

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

    def set_response_with_html(self):
        # Get current url and set response to the HTML received
        url = self.get_current_url()
        try:
            response = requests.get(url, timeout=10).text
            self.response = response
            self.add_url_counter()
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema,
                requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,
                requests.exceptions.Timeout, requests.exceptions.TooManyRedirects) as e:
            print(f'Link Error: {e}')

    def set_email_dict_default(self):
        # adds an entry into the email dict, 'base_url': []
        self.email_dict.setdefault(self.get_current_base_url(), [])

    def set_default_url_counter(self):
        self.url_counter.setdefault(self.get_current_base_url(), 0)

    def set_default_queue_counter(self):
        # set queue counter to default, 'url_base': 1
        self.queue_counter.setdefault(self.get_current_base_url(), 1)

    def get_email_with_html_parser(self):
        # For some reason using beautiful soup automatically converts unicode chars into letters
        # So using beautiful soup and looping through each tag and checking if the tag contains an email that has
        # been decoded with beautiful soup is the best option, make this comment prettier in the future please
        soup = BeautifulSoup(self.response, features='html.parser')
        email_list = []

        for anchor in soup.find_all('a'):
            print(anchor)
            new_emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+",
                                             str(anchor), re.I)
            if new_emails:
                if len(new_emails) > 2:
                    print('More than 1 email found in link. Refer to .get_email_with_html_parser')
                    print(new_emails)

                new_emails = new_emails[0]
                if new_emails not in email_list:
                    email_list.append(new_emails.lower())
        return email_list

    def get_email_from_response(self):
        # Uses the email regex to extract the emails from response and adds the new emails to list if it isn't already
        # in the list

        # get new emails from response html
        new_emails = list(set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+",
                                         self.response, re.I)))
        if new_emails:
            new_emails = [i.lower() for i in new_emails]
            self.add_email(new_emails)
        else:
            new_emails = self.get_email_with_html_parser()
            # Repeated code from line 119, create a method to add emails to email_dict
            if new_emails:
                self.add_email(new_emails)
            else:
                print(f'No Emails Found with Beautiful Soup Parser')

    def add_email(self, new_email_list):
        # If email in list isn't in email dict, add it, else, remove it from email list
        try:
            emails_frm_email_dict = self.email_dict[self.get_current_base_url()]
        except KeyError:
            self.set_email_dict_default()
            emails_frm_email_dict = self.email_dict[self.get_current_base_url()]
        for email in new_email_list:
            if email in emails_frm_email_dict:
                continue
            emails_frm_email_dict.append(email)

    def add_to_new_urls(self, url):
        # Add another url to new_urls
        self.new_urls.append(url)

    def add_url_counter(self):
        # increment the url counter in url_counter by 1
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
        # check link for criteria
        exclude_ext = ['image', 'pdf', 'jpg', 'png', 'gif', 'xlsx', 'spx',
                       'mp3', 'csv', 'wma', 'provider', 'specialtie', 'pptx',
                       'asp', 'mp4', 'download', 'javascript', 'tel:', 'pdf',
                       'specialty']

        for extension in exclude_ext:
            # skips over links with the following keywords from exclude_ext
            if extension in self.poss_link:
                # extension is in link
                return False
        if self.poss_link in self.processed_urls:
            # link is already in the processed urls
            return False
        elif self.poss_link in self.new_urls:
            # link is already in new urls
            return False
        elif self.poss_link.startswith('mailto:'):
            # link is a mailto: link, extract email from mailto:, and add it to the email list if not already in there
            email_from_link = self.poss_link[7:]
            self.add_email([email_from_link])
            return False
        elif self.get_current_base_url() not in self.poss_link:
            # Base url is not in the link, ex. 'http://instagram.com/company_profile
            # print(f'Link: {self.poss_link} doesnt have url base {self.get_current_base_url()}')
            return False
        else:
            return True

    def get_new_urls_from_html(self):
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
                    print(self.poss_link, file=sys.stderr)
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

    @classmethod
    def print_emails(cls):
        # Print out all of the emails for each entry in the email dictionary
        for link, email_list in cls.email_dict.items():
            print(f'Emails Found: {link}')
            for email in email_list:
                print(f'\t\t{email}')



