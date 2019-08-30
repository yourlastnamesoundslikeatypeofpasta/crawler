"""A class version of main.py"""
import os
import shelve
import string
import sys
import time
from collections import deque
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from base_url import base_url


class Crawl:
    """A class the crawls and scrapes a given new_urls"""

    # Dictionary that stores the number of times a base_url has been processed {'base_url': 21}
    url_counter = {}

    # Dictionary that stores the number of links added to from scraped links {'base_url': 45}
    queue_counter = {}

    # List of urls that have been processed
    processed_urls = []

    # Default max number of links to add to the new_urls list
    url_cap = 1500

    # Default sleep time (in seconds) between each crawl
    sleep_time = 10

    # A debugging dictionary, {link_origin: [new_link, new_link_1, new_link_3]}
    debug_dict = {}

    # Buggy new_urls list
    buggy_url_list = []

    # def __init__(self, new_urls, regex):
    def __init__(self, session_name, new_urls):
        self.session_name = session_name
        # Check if new_urls is a string and over-write it as a list if it is
        if isinstance(new_urls, str):
            new_urls = [new_urls.strip().lower()]

        # Create a deque from the new_urls list
        self.new_urls = deque(new_urls)

        # elif regex == 'CAFR':
        #     self.regex = r"(Comprehensive Annual Financial Report)|(CAFR)"

        # Where HTML text is stored for the current new_urls
        self.response = None

        # The current new_urls being processed
        self.current_url = None

        # A possible link that may have been found from the HTML
        self.poss_link = None

        # Create a default dictionary entries
        for link in new_urls:
            self.url_counter.setdefault(base_url(link), 0)
            self.queue_counter.setdefault(base_url(link), 0)

    def get_current_base_url(self):
        """
        Get the current base new_urls.
        :return: Base new_urls.
        """
        return base_url(self.current_url)

    def get_new_urls_from_html(self):
        """
        Get new urls from the <a> tags in html, verify them,
         and if they're verified add them to new_urls list.
        :return: None
        """
        # get new new_urls links from html and add them to the new urls deque()
        soup = BeautifulSoup(self.response, features='html.parser')

        # Go through every link in html and add it to list
        for anchor in soup.find_all('a'):

            # check if base new_urls is capped
            if self.queue_counter.get(self.get_current_base_url()) >= self.url_cap:
                url_base = self.get_current_base_url()
                url_base_count = self.queue_counter[self.get_current_base_url()]
                print(f'Queue Capped: {url_base}: {url_base_count}')
                break

            try:
                if 'href' in anchor.attrs or anchor.attrs['href'].find('mailto') == -1:
                    link = anchor.attrs['href']

                    # Occasionally anchor.attrs['href'] == None
                    if link is not None:
                        self.poss_link = link
            except KeyError:
                """The tags that cause KeyErrors are typically in this fashion
                  KeyError: Anchor: <a name="1412"></a>"""
                continue

            # Resolve relative links
            try:
                if self.poss_link.startswith('/'):
                    # ex. /catalog/books/index.html
                    self.poss_link = urljoin(self.current_url, self.poss_link)
                elif self.poss_link[0] in string.ascii_letters and '/' not in self.poss_link:
                    # ex. page-1.html
                    self.poss_link = urljoin(self.current_url, self.poss_link)
                elif self.poss_link.startswith('..'):
                    # ex. ../../page-1.html
                    # self.poss_link = find_abs_path(self.current_url, self.poss_link)
                    self.poss_link = urljoin(self.current_url, self.poss_link)
                elif self.poss_link[0] in string.ascii_letters and '/' in self.poss_link:
                    # ex. content/media/index.html
                    self.poss_link = urljoin(self.current_url, self.poss_link)
            except IndexError as err:
                print(f'Error: {err}', file=sys.stderr)
                print(f'poss link: {self.poss_link}', file=sys.stderr)
                print(f'Anchor: {anchor}', file=sys.stderr)

            # lower poss_link to avoid duplicate links with different casing
            self.poss_link = self.poss_link.lower()

            # Add the new_urls to the new_urls and print out that a link was added
            if self.is_poss_link_a_link():

                # Create an entry in the debug dictionary
                self.debug_dict.setdefault(self.current_url, [self.poss_link])
                if self.poss_link not in self.debug_dict[self.current_url]:
                    self.debug_dict[self.current_url].append(self.poss_link)

                # add the link to new_urls
                self.add_to_new_urls(self.poss_link)
                print(f'New URL Added: {self.poss_link}')
                self.add_queue_counter()

    def get_total_urls_scraped(self):
        """
        Get the total urls scraped.
        :return: the number of urls scraped.
        """
        # get the total amount of links scraped
        count = 0
        for i in self.url_counter.values():
            count += i
        return count

    def set_new_urls(self, url_list):
        """
        Update new_urls with a list of new urls.
        :param url_list: a string or list of new urls to crawl
        :return: None
        """
        if type(url_list) == list:
            self.new_urls = deque(url_list)
            print(f'new_urls set to {self.new_urls}')
        if type(url_list) == str:
            self.new_urls = deque([url_list])
            print(f'new_urls set to {self.new_urls}')

    def set_current_url(self):
        """
        Set current_url to the first object from new_urls
        and then add that new_urls to the processed_urls list.
        :return: None
        """
        url = self.new_urls.popleft()
        self.processed_urls.append(url)
        self.current_url = url

    def set_response_with_html(self):
        """
        Set response with the html from the current_url.
        :return: None
        """
        # Get current new_urls and set response to the HTML received
        url = self.current_url
        try:
            # TODO: Look into adding headers and proxies.
            #  Maybe a method to turn proxies on or off, default off
            response = requests.get(url, timeout=10)
            status_code = response.status_code

            if status_code != 200:
                # Add the current new_urls and new link to the the debug dictionary and print out the status code
                print(f'Status Code Error: {self.current_url}: {status_code}', file=sys.stderr)
                self.buggy_url_list.append(self.current_url)
                self.response = None
            else:
                self.response = response.text
                self.add_url_counter()
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema,
                requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,
                requests.exceptions.Timeout, requests.exceptions.TooManyRedirects) as e:
            print(f'Link Error: {e}')

    def add_to_new_urls(self, url):
        """
        Add a new new_urls to new_urls.
        :param url: The new new_urls
        :return: None
        """
        # Add another new_urls to new_urls
        self.new_urls.append(url)

    def add_url_counter(self):
        """
        Increment the base_url in url_counter by 1
        :return: None
        """
        # increment the new_urls counter in url_counter by 1
        self.url_counter[self.get_current_base_url()] += 1

    def add_queue_counter(self):
        """
        Increment the url_base in queue_counter by one.
        :return: None
        """
        self.queue_counter[self.get_current_base_url()] += 1

    def is_url_capped(self):
        """
        Check if the new_urls is capped at the currently set url_cap.
        :return: True if the new_urls is capped, False if it isn't
        """
        if self.url_counter.get(self.get_current_base_url()) >= self.url_cap:
            return True
        return False

    def is_poss_link_a_link(self):
        """
        Check if self.poss_link is a valid relative link.
        :return: True if the relative link is value; False if the relative link isn't.
        """
        exclude_ext = ['image', 'pdf', 'jpg', 'png', 'gif', 'xlsx',
                       'mp3', 'csv', 'wma', 'provider', 'specialtie', 'pptx',
                       'mp4', 'download', 'javascript', 'tel:', 'pdf', 'ppt',
                       'specialty']

        for extension in exclude_ext:
            # skips over links with the following keywords from exclude_ext
            if extension in self.poss_link:
                # extension is in link
                return False
        if self.poss_link in self.processed_urls:
            # link is already in the processed urls
            return False
        if self.poss_link in self.new_urls:
            # link is already in new urls
            return False
        if self.get_current_base_url() not in self.poss_link:
            # Base new_urls is not in the link, ex. 'http://instagram.com/company_profile
            return False
        if 'mailto:' in self.poss_link:
            return False
        return True
    
    def save_progress(self):
        """
        Save the variables new_urls, response, current_url, poss_link,
        url_counter, queue_counter, url_cap, sleep_time, debug_dict,
        and buggy_url_list with shelve.
        :return: None
        """
        with shelve.open(f'./save/{self.session_name}.db') as save:
            save['main'] = {
                'session_name': self.session_name,
                'new_urls': self.new_urls,
                'response': self.response,
                'current_url': self.current_url,
                'poss_link': self.poss_link,
                'url_counter': self.url_counter,
                'queue_counter': self.queue_counter,
                'url_cap': self.url_cap,
                'sleep_time': self.sleep_time,
                'debug_dict': self.debug_dict,
                'buggy_url_list': self.buggy_url_list,
            }

    def crawl(self):
        """
        Crawl the deque of urls
        :return: None
        """
        
        # begin crawling
        try:
            while len(self.new_urls):
                print(f'Session - {self.session_name}')
                status = 'crawling...'
                print(f'Crawl Status - {status}')
                print(f'Crawls Completed: {self.get_total_urls_scraped()}')
                print(f'Crawl Queue: {len(self.new_urls)}')
                self.print_buggy_links()
                self.set_current_url()
                print(f'Processing: {self.current_url}', file=sys.stderr)
                self.set_response_with_html()
                if self.response:
                    self.get_new_urls_from_html()
                    time.sleep(self.sleep_time)
                self.save_progress()
                self.clear()
                time.sleep(.1)

            # crawl complete
            self.save_progress()
            print(f'Session - {self.session_name}')
            status = 'crawl complete'
            print(f'Crawl Status - {status}')
            print(f'Crawls Completed: {self.get_total_urls_scraped()}')
            self.print_buggy_links()
        except KeyboardInterrupt:
            self.print_buggy_links()

    @classmethod
    def from_save(cls, name_session):
        with shelve.open(f'./save/{name_session}.db', flag="r") as save:
            save_dict = save['main']
            new_urls = save_dict.get('new_urls')
            session_name = save_dict['session_name']
            cls.response = save_dict.get('response')
            cls.current_url = save_dict.get('current_url')
            cls.poss_link = save_dict.get('poss_link')
            cls.url_counter = save_dict.get('url_counter')
            cls.queue_counter = save_dict.get('queue_counter')
            cls.url_cap = save_dict.get('url_cap')
            cls.sleep_time = save_dict.get('sleep_time')
            cls.debug_dict = save_dict.get('debug_dict')
            cls.buggy_url_list = save_dict.get('buggy_url_list')
            return cls(session_name, new_urls)

    @classmethod
    def print_buggy_links(cls):
        """
        Print out the buggy links and the urls from which they came from. This is for debugging purposes.
        :return:
        """
        if cls.buggy_url_list:
            print('Buggy Links:')
            for url, links in cls.debug_dict.items():
                buggy_link_list = []
                for link in links:
                    if link in cls.buggy_url_list:
                        buggy_link_list.append(link)
                if buggy_link_list:
                    print(f'\tLink Origin: {url}')
                    for link in buggy_link_list:
                        print(f'\t\tLink: {link}')
        else:
            print('No buggy links found!')

    @staticmethod
    def clear():
        """
        Clears the screen of the terminal.
        :return: None
        """
        os.system('clear')

    # TODO: Make a class method that writes the results to a json dictionary
    # TODO: Write a method that will print out the stats