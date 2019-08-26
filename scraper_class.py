"""A class version of main.py"""
import re
import sys
import string
import time
from collections import deque
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from base_url import base_url
from find_abs_path import find_abs_path


class Scraper:
    # Dictionary that stores emails {'base_url': ['email_0', 'email_1']}
    email_dict = {}

    # Dictionary that stores the number of times a base_url has been processed {'base_url': 21}
    url_counter = {}

    # Dictionary that stores the number of links added to from scraped links {'base_url': 45}
    queue_counter = {}

    # List of urls that have been processed
    processed_urls = []

    # Default max number of links to add to the new_urls list
    url_cap = 1500

    # Default sleep time (in seconds) between each scrape
    sleep_time = 10

    def __init__(self, url):
        # Check if url is a string and over-write it as a list if it is
        if type(url) == str:
            url = [url]

        # Create a deque from the url list
        self.new_urls = deque(url)

        # Where HTML text is stored for the current url
        self.response = None

        # The current url being processed
        self.current_url = None

        # A possible link that may have been found from the HTML
        self.poss_link = None

        # Create a default dictionary entry for each website in email_dict, url_counter, queue_counter
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

    def get_email_with_html_parser(self):
        # TODO: Look into turning this into a static method
        # For some reason using beautiful soup automatically converts unicode chars into letters
        # So using beautiful soup and looping through each tag and checking if the tag contains an email that has
        # been decoded with beautiful soup is the best option, make this comment prettier in the future please
        soup = BeautifulSoup(self.response, features='html.parser')
        email_list = []

        for anchor in soup.find_all('a'):
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
            if new_emails:
                self.add_email(new_emails)

    # TODO: Look into creating different regex for different information that can be scraped from a page

    def get_new_urls_from_html(self):
        # get new url links from html and add them to the new urls deque()
        soup = BeautifulSoup(self.response, features='html.parser')

        # Go through every link in html and add it to list
        for anchor in soup.find_all('a'):

            # check if base url is capped
            if self.queue_counter.get(self.get_current_base_url()) >= self.url_cap:
                print(f'Queue Capped: {self.get_current_base_url()}: {self.queue_counter[self.get_current_base_url()]}')
                break

            try:
                if 'href' in anchor.attrs or anchor.attrs['href'].find('mailto') == -1:
                    self.poss_link = anchor.attrs['href']
            except KeyError:
                # KeyErrors are typically in this fashion and aren't the links we're looking for.
                #   KeyError: Anchor: <a class="dnnSearchBoxClearText" title="Clear search text"></a>
                #   KeyError: Anchor: <a name="1404"></a>
                #   KeyError: Anchor: <a name="1410"></a>
                #   KeyError: Anchor: <a name="1412"></a>
                continue

            # Resolve relative links
            if self.poss_link.startswith('http'):
                # TODO: Comment
                pass
            elif self.poss_link.startswith('/'):
                # ex. /catalog/books/index.html
                self.poss_link = self.get_current_base_url() + self.poss_link
            elif self.poss_link[0] in string.ascii_letters and '/' not in self.poss_link:
                # TODO: Comment
                new_url_list = self.current_url.split('/')
                del new_url_list[-1]
                new_url_list.append(self.poss_link)
                self.poss_link = '/'.join(new_url_list)
            elif self.poss_link.startswith('..'):
                # TODO: Comment
                self.poss_link = find_abs_path(self.current_url, self.poss_link)  # FIXME: Not working on some links
                # self.poss_link = urljoin(self.current_url, self.poss_link)  # TESTING!!!
                # TODO: Use urllib.parse.join instead
                #       https://www.reddit.com/r/learnpython/comments/cupusi/web_crawling_resolving_relative_links_question/exx45tg?utm_source=share&utm_medium=web2x
            elif self.poss_link[0] in string.ascii_letters and '/' in self.poss_link:
                # TODO: Comment
                self.poss_link = self.get_current_base_url() + self.poss_link

            # check link criteria, .is_link, placeholder
            if self.is_poss_link_a_link():
                self.add_to_new_urls(self.poss_link)
                print(f'New URL Added: {self.poss_link}')
                self.add_queue_counter()

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
            # TODO: Look into adding headers and proxies. Maybe a method to turn proxies on or off, default off
            response = requests.get(url, timeout=10)
            status_code = response.status_code
            if status_code != 200:
                print(f'Status Code Error: {self.current_url}: {status_code}', file=sys.stderr)
            self.response = response.text
            self.add_url_counter()
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema,
                requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,
                requests.exceptions.Timeout, requests.exceptions.TooManyRedirects) as e:
            print(f'Link Error: {e}')

    def add_email(self, new_email_list):
        # If email in list isn't in email dict, add it, else, remove it from email list
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
        self.queue_counter[self.get_current_base_url()] += 1

    def is_url_capped(self):
        # Return True if the url is capped, False if it isn't
        if self.url_counter.get(self.get_current_base_url()) >= self.url_cap:
            return True
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
        elif 'mailto:' in self.poss_link:  # TODO: TEST THIS AND MAKE SURE IT DOESN'T AVOID LINKS IT SHOULDN'T
            return False
        else:
            return True

    def scrape(self):
        try:
            while len(self.new_urls):
                self.set_current_url()
                print(f'Processing: {self.current_url}', file=sys.stderr)
                self.set_response_with_html()
                self.get_email_from_response()
                self.get_new_urls_from_html()
                print(f'Sleeping: {self.sleep_time} seconds')
                time.sleep(self.sleep_time)
            self.print_emails()
        except KeyboardInterrupt:
            self.print_emails()

    @classmethod
    def print_emails(cls):
        # Print out all of the emails for each entry in the email dictionary
        for link, email_list in cls.email_dict.items():
            if email_list:
                print(f'Emails Found: {link}')
                for email in email_list:
                    print(f'\t\t{email}')
            else:
                print(f'No Emails Found: {link}')

    # TODO: Make a class method that writes the emails to a json dictionary

