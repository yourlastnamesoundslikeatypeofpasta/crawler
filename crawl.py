"""A class version of main.py"""
import os
import shelve
import string
import sys
import time
from collections import deque
from urllib.parse import urljoin
from sys import stdout
from random import randint

import requests
from bs4 import BeautifulSoup

from base_url import base_url
from get_website_name import get_web_name


class Crawl:
    """A class the crawls and scrapes a given new_urls"""

    # todo: sum up these class variables into one large dict

    # Dictionary that stores the number of times a base_url has been processed {'base_url': 21}
    url_counter = {}

    # Dictionary that stores the number of links added to from scraped links {'base_url': 45}
    queue_counter = {}

    # List of urls that have been processed
    processed_urls = []

    # Default max number of links to add to the new_urls list
    url_cap = 1500
    # url_cap = 50

    # Default sleep time (in seconds) between each crawl
    sleep_time = 0

    # A debugging dictionary, {link_origin: [new_link, new_link_1, new_link_3]}
    debug_dict = {}

    # Buggy new_urls list
    buggy_url_list = []

    def __init__(self, new_urls):
        # bypass get_web_name if loading up a previous save
        if isinstance(new_urls, str):
            self.session_name = get_web_name(new_urls)

            # Create a default dictionary entries
            self.url_counter.setdefault(self.session_name, 0)
            self.queue_counter.setdefault(self.session_name, 0)

        # Create a deque from the new_urls list
        if not isinstance(new_urls, deque):
            # create a deque if not loading from a save
            self.new_urls = deque([new_urls])
        else:
            self.new_urls = new_urls

        # Where HTML text is stored for the current new_urls
        self.response = None

        # The current new_urls being processed
        self.current_url = None

        # A possible link that may have been found from the HTML
        self.poss_link = None

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
        try:
            soup = BeautifulSoup(self.response, features='html.parser')
        except TypeError:
            return

        if soup:
            # Go through every link in html and add it to list
            for anchor in soup.find_all('a'):

                # check if base new_urls is capped
                try:
                    if self.queue_counter.get(self.session_name) >= self.url_cap:
                        break
                except TypeError:
                    print(f'TypeError: Line 91 did not work, Session Name: {self.session_name}, Current Url: {self.current_url}, Possible Link: {self.poss_link}')

                try:
                    if 'href' in anchor.attrs or anchor.attrs['href'].find('mailto') == -1:
                        link = anchor.attrs['href']

                        # Occasionally anchor.attrs['href'] == None
                        if link:
                            self.poss_link = link
                except KeyError:
                    """The tags that cause KeyErrors are typically in this fashion
                      KeyError: Anchor: <a name="1412"></a>"""
                    continue

                # Resolve relative links
                try:
                    if ('/' in self.poss_link) or ('..' in self.poss_link) or ('./' in self.poss_link) or \
                            (self.session_name not in self.poss_link):
                        # ex. /catalog/books/index.html
                        self.poss_link = urljoin(self.current_url, self.poss_link)
                except IndexError as err:
                    # print(f'Error: {err}', file=sys.stderr)
                    # print(f'poss link: {self.poss_link}', file=sys.stderr)
                    # print(f'Anchor: {anchor}', file=sys.stderr)
                    continue

                # Add the new_urls to the new_urls and print out that a link was added
                if self.is_poss_link_a_link():

                    # Create an entry in the debug dictionary
                    self.debug_dict.setdefault(self.current_url, [self.poss_link])
                    if self.poss_link not in self.debug_dict[self.current_url]:
                        self.debug_dict[self.current_url].append(self.poss_link)

                    # add the link to new_urls
                    self.add_to_new_urls(self.poss_link)
                    try:  # fixme: fix this key error - should be working now, test me
                        self.add_queue_counter()
                    except KeyError:
                        print(f'KeyError: Line 148 did not work, Session Name: {self.session_name}, Current Url: {self.current_url}, Possible Link: {self.poss_link}')

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
            headers = {
                'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                               'AppleWebKit/537.36 (KHTML, like Gecko)'
                               'Chrome/76.0.3809.100 Safari/537.36')
            }
            response = requests.get(url, headers=headers, timeout=5)
            # todo: add a way to check the content type and content length and then filter from with this function
            status_code = response.status_code

            # Don't set response if the content is above a certain size in bytes
            if len(response.content) >= 20_000_000:
                self.response = None
            elif response.history and response.ok:
                # if the response was redirected to a new url and 200 status code
                self.current_url = response.url
                self.response = response.text
                self.add_url_counter()
            elif response.ok:
                # if the response has a successful status code
                try:
                    self.response = response.text
                    self.add_url_counter()
                except KeyError:
                    self.buggy_url_list.append(self.current_url)
                    self.response = None
            else:
                # if the response was redirected, or had a client or server error
                self.buggy_url_list.append(self.current_url)
                self.response = None
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema,
                requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,
                requests.exceptions.Timeout, requests.exceptions.TooManyRedirects) as e:
            self.response = None

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
        # self.url_counter[self.get_current_base_url()] += 1

        try:
            self.url_counter[self.session_name] += 1
        except KeyError:
            print('freagin BUGGY CODE:', self.current_url, self.poss_link, self.session_name)

    def add_queue_counter(self):
        """
        Increment the url_base in queue_counter by one.
        :return: None
        """
        self.queue_counter[self.session_name] += 1

    def is_url_capped(self):
        """
        Check if the new_urls is capped at the currently set url_cap.
        :return: True if the new_urls is capped, False if it isn't
        """
        if self.url_counter.get(self.session_name) >= self.url_cap:
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
        if self.session_name not in self.poss_link:
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
        # create the directory if it doesn't exit
        directory_path = './save/crawl'
        if not os.path.exists(directory_path):
            os.mkdir(directory_path)

        # save dictionary
        with shelve.open(f'./save/crawl/{self.session_name}.db') as save:
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
        session = self.session_name
        status = 'crawling'
        try:
            while len(self.new_urls):
                self.set_current_url()
                queue = len(self.new_urls)
                processing = self.current_url
                stdout.write(f'|Session:{session}|Status:{status}|Queue:{queue}|Processing:{processing}\r')
                self.set_response_with_html()
                if self.response:
                    self.get_new_urls_from_html()
                    time.sleep(self.sleep_time)
                self.save_progress()
                time.sleep(.1)

            # crawl complete
            self.save_progress()
            status = 'crawl complete'
            print(f'|Session:{session}|Status:{status}|Urls Scanned: {len(self.processed_urls)}')
            self.print_buggy_links()
        except KeyboardInterrupt:
            self.print_buggy_links()
        return {'session_name': self.session_name, 'url_counter': self.url_counter, 'debug_dict': self.debug_dict}

    @staticmethod
    def from_save(name_session):
        with shelve.open(f'./save/crawl/{name_session}.db', flag="r") as save:
            save_dict = save['main']
            new_urls = save_dict.get('new_urls')
            session_name = save_dict['session_name']
            response = save_dict.get('response')
            current_url = save_dict.get('current_url')
            poss_link = save_dict.get('poss_link')
            url_counter = save_dict.get('url_counter')
            queue_counter = save_dict.get('queue_counter')
            url_cap = save_dict.get('url_cap')
            sleep_time = save_dict.get('sleep_time')
            debug_dict = save_dict.get('debug_dict')
            buggy_url_list = save_dict.get('buggy_url_list')

            # create Crawl object to return
            url = Crawl(new_urls)
            url.session_name = session_name
            url.response = response
            url.current_url = current_url
            url.poss_link = poss_link
            url.url_counter = url_counter
            url.queue_counter = queue_counter
            url.url_cap = url_cap
            url.sleep_time = sleep_time
            url.debug_dict = debug_dict
            url.buggy_url_list = buggy_url_list
            return url

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

    # TODO: Make a class method that writes the results to a text file
