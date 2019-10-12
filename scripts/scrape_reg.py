"""A sub-class of Crawl. Scrape crawled pages with a regular expression"""
import os
import re
import sys
import shelve
import time
import tkinter
from tkinter import filedialog

from bs4 import BeautifulSoup

from scripts.base_url import base_url
from scripts.get_website_name import get_web_name
from scripts.crawl import Crawl


class ScrapeReg(Crawl):
    """
    A sub-class of Crawl. Scrape crawled pages with a regular expression
    """
    result_dict = {}

    def __init__(self, new_urls, regex):
        super().__init__(new_urls)
        if isinstance(new_urls, str):
            self.session_name = get_web_name(new_urls)
        self.regex = regex

        # Create a default dictionary entry for each web domain in result_dict
        if isinstance(new_urls, str):
            new_urls = [new_urls]
        for link in new_urls:
            print('blag', self.session_name, link, new_urls)
            self.result_dict.setdefault(base_url(link), [])

    def get_result_with_html_parser(self):
        """
        If get_result_from_response doesn't work, then go through each <a> tag,
        use regex in each tag, if the tag has a results add it to the result_list.

        For some reason using beautiful soup automatically converts
        unicode chars into letters. So using beautiful soup and looping through
        each tag and checking if the tag contains a result that has been decoded
        with beautiful soup is the best option, make this comment prettier in
        the future please
        :return: result_list
        """
        soup = BeautifulSoup(self.response, features='html.parser')
        result_list = []

        for anchor in soup.find_all('a'):
            new_results = re.findall(self.regex,
                                     str(anchor), re.I)
            if new_results:
                if len(new_results) > 2:
                    print('More than 1 result found in link. Refer to .get_result_with_html_parser')
                    print(new_results)

                new_results = new_results[0]
                if new_results not in result_list:
                    result_list.append(new_results.lower())
        return result_list

    def get_result_from_response(self):
        """
        Get results from the html stored in response using regex and
        use add_result to add the result to the result_dict or
        use get_result_with_html_parser and regex to look for
        a result in the <a> tags
        :return: None
        """
        # get new results from response html
        new_results_list = list(set(re.findall(self.regex,
                                               self.response, re.I)))

        if new_results_list:
            try:
                new_results_list = [i.lower() for i in new_results_list]
            except AttributeError as e:
                print(f'AttributeError: {e}')
                sys.exit()
            self.add_result(new_results_list)
        else:
            new_results_list = self.get_result_with_html_parser()
            if new_results_list:
                self.add_result(new_results_list)

    def add_result(self, new_result_list):
        """
        Add results found to result_dict.
        :param new_result_list: List of newly found results.
        :return: None
        """
        # If result in the list isn't in the result dict, add it, else, remove it from new_result_list
        result_from_rslt_dict = self.result_dict[self.get_current_base_url()]
        new_result_list = [i.lower() for i in new_result_list]
        for result in new_result_list:
            if result in result_from_rslt_dict:
                continue
            result_from_rslt_dict.append(result)

    def save_progress(self):
        """
                Save the variables new_urls, response, current_url, poss_link,
                url_counter, queue_counter, url_cap, sleep_time, debug_dict,
                and buggy_url_list with shelve.
                :return: None
        """
        # verify that the directory: ./save/scrape_reg exists, create it, if not
        path = './save/scrape_reg/'
        if not os.path.exists(path):
            os.mkdir(path)

        # save the progress
        shelve_file = f'{path}{self.session_name}.db'
        with shelve.open(shelve_file) as save:
            save['main'] = {
                'session_name': self.session_name,
                'new_urls': self.new_urls,
                'regex': self.regex,  # regex added to .save_progress
                'result_dict': self.result_dict,  # result_dict added to .save_progress
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

    @staticmethod
    def from_save(name_session):
        with shelve.open(f'./save/scrape_reg/{name_session}.db', flag="r") as save:
            save_dict = save['main']
            session_name = save_dict['session_name']
            new_urls = save_dict.get('new_urls')
            regex = save_dict.get('regex')  # regex added to .from_save
            result_dict = save_dict['result_dict']  # result_dict added to .from_save
            response = save_dict.get('response')
            current_url = save_dict.get('current_url')
            poss_link = save_dict.get('poss_link')
            url_counter = save_dict.get('url_counter')
            queue_counter = save_dict.get('queue_counter')
            url_cap = save_dict.get('url_cap')
            sleep_time = save_dict.get('sleep_time')
            debug_dict = save_dict.get('debug_dict')
            buggy_url_list = save_dict.get('buggy_url_list')

            # create a ScrapeReg object
            url = ScrapeReg(new_urls, regex)
            url.session_name = session_name
            url.result_dict = result_dict
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
    def print_results(cls):
        """
        Print out all results found for each link.
        :return:
        """
        # check if the result_dict has any values within it
        values = [i for i in cls.result_dict.values() if i]
        if values:
            print('Results Found:')
            for link, result_list in cls.result_dict.items():
                if result_list:
                    print(f'\tUrl: {link}')
                    for result in result_list:
                        print(f'\t\tResult: {result}')
        else:
            print('No results found!')

    @classmethod
    def write_to_txt(cls):
        """
        When crawl is complete, write the contents of result_dict to a text file.
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

        # Write results to results.txt
        with open(file_path + '/results.txt', 'w') as results:
            if cls.result_dict:
                for link, result_list in cls.result_dict.items():
                    if result_list:
                        results.write(f'Results for: {link}\n')
                        for result in result_list:
                            if result == result_list[-1]:
                                results.write(f'{result}\n\n')
                                break
                            results.write(f'{result}\n')
                print('Results saved!')
            else:
                print('No Results to save!')

    def crawl(self):

        def get_result_count():
            """
            Get the number of results found.
            :return: an integer of the number of results found.
            """
            results = [i for i in self.result_dict.values() if i]
            result_count = 0
            if results:
                for result_list in self.result_dict.values():
                    if result_list:
                        for result in result_list:
                            result_count += 1
                return result_count
            else:
                return 0

        # begin crawl
        session = self.session_name
        try:
            while len(self.new_urls):
                self.set_current_url()
                queue = len(self.new_urls)
                processing = self.current_url
                result_count = get_result_count()
                status = 'crawling'
                # print(f'|Session:{session}|Status:{status}|Queue:{queue}|Results:{result_count}|Processing:{processing}', end='\r') not printing with end
                print(f'|Session:{session}|Status:{status}|Queue:{queue}|Results:{result_count}|Processing:{processing}')
                self.set_response_with_html()
                if self.response:
                    self.get_result_from_response()
                    self.get_new_urls_from_html()
                    time.sleep(self.sleep_time)
                self.save_progress()

            # crawl complete
            self.save_progress()
            print(f'Session - {self.session_name}')
            status = 'crawl complete'
            print(f'Crawl Status - {status}')
            print(f'Crawls Completed: {self.get_total_urls_scraped()}')
            self.print_results()
            self.print_buggy_links()
            result_list = list(self.result_dict.values())[0]
            print('Output', self.session_name, result_list)
            return self.session_name, result_list
        except KeyboardInterrupt:
            self.print_results()
            self.print_buggy_links()
