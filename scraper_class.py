"""A class version of main.py"""
import re
import os
import sys
import string
import shelve
import time
import tkinter
from collections import deque
from urllib.parse import urljoin
from tkinter import filedialog

import requests
from bs4 import BeautifulSoup

from base_url import base_url


class Scraper:
    """A class the crawls and scrapes a given url"""
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

    # A debugging dictionary, {link_origin: [new_link, new_link_1, new_link_3]}
    debug_dict = {}

    # Buggy url list
    buggy_url_list = []

    def __init__(self, url):
        # Check if url is a string and over-write it as a list if it is
        if type(url) == str:
            url = [url.rstrip()]

        # todo: create a session_name attribute

        # Create a deque from the url list
        self.new_urls = deque(url)

        # Where HTML text is stored for the current url
        self.response = None

        # The current url being processed
        self.current_url = None

        # A possible link that may have been found from the HTML
        self.poss_link = None

        # Create a default dictionary entry for each website in email_dict
        for link in url:
            self.email_dict.setdefault(base_url(link), [])
            self.url_counter.setdefault(base_url(link), 0)
            self.queue_counter.setdefault(base_url(link), 0)

    def get_current_base_url(self):
        """
        Get the current base url.
        :return: Base url.
        """
        return base_url(self.current_url)

    def get_email_with_html_parser(self):
        """
        If get_email_from_response doesn't work, then go through each <a> tag,
        use regex in each tag, if the tag has an email add it to the email_list.

        For some reason using beautiful soup automatically converts
        unicode chars into letters. So using beautiful soup and looping through
        each tag and checking if the tag contains an email that has been decoded
        with beautiful soup is the best option, make this comment prettier in
        the future please
        :return: email_list
        """
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
        """
        Get emails from the html stored in response using regex and
         uses add_email to add the email to the email_dict.
        :return: None
        """
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

    def get_new_urls_from_html(self):
        """
        Get new urls from the <a> tags in html, verify them,
         and if they're verified add them to new_urls list.
        :return: None
        """
        # get new url links from html and add them to the new urls deque()
        soup = BeautifulSoup(self.response, features='html.parser')

        # Go through every link in html and add it to list
        for anchor in soup.find_all('a'):

            # check if base url is capped
            if self.queue_counter.get(self.get_current_base_url()) >= self.url_cap:
                url_base = self.get_current_base_url()
                url_base_count = self.queue_counter[self.get_current_base_url()]
                print(f'Queue Capped: {url_base}: {url_base_count}')
                break

            try:
                if 'href' in anchor.attrs or anchor.attrs['href'].find('mailto') == -1:
                    link = anchor.attrs['href']

                    # Occasionally anchor.attrs['href'] == None
                    if len(link) > 1:
                        self.poss_link = anchor.attrs['href']
            except KeyError:
                """The tags that cause KeyErrors are typically in this fashion
                  KeyError: Anchor: <a name="1412"></a>"""
                continue

            # Resolve relative links
            try:
                if self.poss_link.startswith('/'):
                    # ex. /catalog/books/index.html
                    # self.poss_link = self.get_current_base_url() + self.poss_link
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

            # Add the url to the new_urls and print out that a link was added
            if self.is_poss_link_a_link():

                # Create an entry in the debug dictionary
                self.debug_dict.setdefault(self.current_url, [self.poss_link])
                if self.poss_link not in self.debug_dict[self.current_url]:
                    self.debug_dict[self.current_url].append(self.poss_link)

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
        :param url_list: a string or list of new urls to scrape
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
        and then add that url to the processed_urls list.
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
        # Get current url and set response to the HTML received
        url = self.current_url
        try:
            # TODO: Look into adding headers and proxies.
            #  Maybe a method to turn proxies on or off, default off
            response = requests.get(url, timeout=10)
            status_code = response.status_code

            if status_code != 200:
                # Add the current url and new link to the the debug dictionary and print out the status code
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

    def add_email(self, new_email_list):
        """
        Add emails found to email_dict.
        :param new_email_list: List of newly found emails.
        :return: None
        """
        # If email in the list isn't in the email dict, add it, else, remove it from email list
        emails_frm_email_dict = self.email_dict[self.get_current_base_url()]
        for email in new_email_list:
            if email in emails_frm_email_dict:
                continue
            emails_frm_email_dict.append(email)

    def add_to_new_urls(self, url):
        """
        Add a new url to new_urls.
        :param url: The new url
        :return: None
        """
        # Add another url to new_urls
        self.new_urls.append(url)

    def add_url_counter(self):
        """
        Increment the base_url in url_counter by 1
        :return: None
        """
        # increment the url counter in url_counter by 1
        self.url_counter[self.get_current_base_url()] += 1

    def add_queue_counter(self):
        """
        Increment the url_base in queue_counter by one.
        :return: None
        """
        self.queue_counter[self.get_current_base_url()] += 1

    def is_url_capped(self):
        """
        Check if the url is capped at the currently set url_cap.
        :return: True if the url is capped, False if it isn't
        """
        if self.url_counter.get(self.get_current_base_url()) >= self.url_cap:
            return True
        return False

    def is_poss_link_a_link(self):
        """
        Check if self.poss_link is a valid relative link.
        :return: True if the relative link is value; False if the relative link isn't.
        """
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
        if self.poss_link in self.new_urls:
            # link is already in new urls
            return False
        if self.poss_link.startswith('mailto:'):
            # link is a mailto: link, extract email from mailto:, and add it to the email list if not already in there
            email_from_link = self.poss_link[7:]
            self.add_email([email_from_link])
            return False
        if self.get_current_base_url() not in self.poss_link:
            # Base url is not in the link, ex. 'http://instagram.com/company_profile
            return False
        if 'mailto:' in self.poss_link:
            return False
        return True

    def save_progress(self, name_session):
        """
        Save the variables new_urls, response, current_url, poss_link,email_dict,
        url_counter, queue_counter, url_cap, sleep_time, debug_dict,
        and buggy_url_list with shelve.
        :return: None
        """
        with shelve.open(f'./save/{name_session}.db') as save:
            save['main'] = {
                'new_urls': self.new_urls,
                'response': self.response,
                'current_url': self.current_url,
                'poss_link': self.poss_link,
                'email_dict': self.email_dict,
                'url_counter': self.url_counter,
                'queue_counter': self.queue_counter,
                'url_cap': self.url_cap,
                'sleep_time': self.sleep_time,
                'debug_dict': self.debug_dict,
                'buggy_url_list': self.buggy_url_list,
            }

    def scrape(self):
        """
        Scrape the link(s) that the user enters and print the results to the screen.
        :return: None
        """
        def get_name_session():
            """
            Get the name of this scrape session from the user.
            :return: a string of the name of the session
            """
            # chars not allowed
            illegal_char_list = ['\\', '/', ':', 'NUL', ':', '*', '"', '<', '>', '|']
            while True:
                ns = input('What would you like to name this scrape session?\n:').lower().strip()

                # check if the name session has any illegal character
                illegal_char = False
                for char in ns:
                    if char in illegal_char_list:
                        print(f'IllegalCharacter: {char}. Your session name cannot have the following characters:')
                        print(','.join(illegal_char_list))
                        illegal_char = True
                        break
                if illegal_char:
                    continue
                else:
                    return ns

        name_session = get_name_session()
        try:
            while len(self.new_urls):
                print(f'Session - {name_session}')
                status = 'scraping'
                print(f'Status - {status}')
                print(f'Urls scraped: {self.get_total_urls_scraped()}')
                print(f'Urls to scrape: {len(self.new_urls)}')
                self.print_emails()
                self.print_buggy_links()
                self.set_current_url()
                print(f'Processing: {self.current_url}', file=sys.stderr)
                self.set_response_with_html()
                if self.response:
                    self.get_email_from_response()
                    self.get_new_urls_from_html()
                    self.save_progress(name_session)
                    time.sleep(self.sleep_time)
                self.save_progress(name_session)
                self.clear()

            # scrape complete
            self.save_progress(name_session)
            print(f'Session - {name_session}')
            status = 'scraping complete'
            print(f'Status - {status}')
            print(f'Urls scraped: {self.get_total_urls_scraped()}')
            self.print_emails()
            self.print_buggy_links()
        except KeyboardInterrupt:
            self.print_emails()
            self.print_buggy_links()

    @classmethod
    def from_save(cls, name_session):
        with shelve.open(f'./save/{name_session}.db', flag="r") as save:
            save_dict = save['main']
            new_urls = save_dict.get('new_urls')
            cls.response = save_dict.get('response')
            cls.current_url = save_dict.get('current_url')
            cls.poss_link = save_dict.get('poss_link')
            cls.email_dict = save_dict.get('email_dict')
            cls.url_counter = save_dict.get('url_counter')
            cls.queue_counter = save_dict.get('queue_counter')
            cls.url_cap = save_dict.get('url_cap')
            cls.sleep_time = save_dict.get('sleep_time')
            cls.debug_dict = save_dict.get('debug_dict')
            cls.buggy_url_list = save_dict.get('buggy_url_list')
            return cls(new_urls)

    @classmethod
    def write_to_txt(cls):
        """
        When crawl is complete, write the contents of email_dict to a text file.
        :return: None
        """

        def get_file_path():
            """
            Open a file dialog window and ask the user where they would like to
            save their results
            :return: a string of the absolute file path
            """
            # Set up the tkinter object
            root = tkinter.Tk()
            root.withdraw()

            # Bring up the dialog window
            curr_path = os.getcwd()
            txt_path = filedialog.askdirectory(parent=root, initialdir=curr_path,
                                               title='Save results to...')
            return txt_path

        # Get file path with a dialog window
        file_path = get_file_path()

        # Write email results to results.txt
        with open(file_path + '/results.txt', 'w') as results:
            if cls.email_dict:
                for link, email_list in cls.email_dict.items():
                    if email_list:
                        results.write(f'Emails for: {link}\n')
                        for email in email_list:
                            if email == email_list[-1]:
                                results.write(f'{email}\n\n')
                                break
                            results.write(f'{email}\n')
                print('Results saved!')
            else:
                print('No Results to save!')

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

    @classmethod
    def print_emails(cls):
        """
        Print out all emails found for each link.
        :return:
        """
        if cls.email_dict:
            print('Emails Found:')
            for link, email_list in cls.email_dict.items():
                if email_list:
                    print(f'\tUrl: {link}')
                    for email in email_list:
                        print(f'\t\t{email}')
        else:
            print('No Emails Found!')

    @staticmethod
    def clear():
        """
        Clears the screen of the terminal.
        :return: None
        """
        os.system('clear')

    # TODO: Look into creating different regex for different information that can be scraped from a page
    # TODO: Make a class method that writes the emails to a json dictionary
    # TODO: Write a method that will print out the stats
