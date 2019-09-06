"""A sub-class of ScrapeReg. Crawl through pages and return links that contain html that match the key/regex"""
import os
import re
import sys
import time

from bs4 import BeautifulSoup

from base_url import base_url
from scrape_reg import ScrapeReg


class LinkKey(ScrapeReg):
    """Crawl through pages and return links that match the key/regex"""

    def __init__(self, new_urls, regex):
        super().__init__(new_urls, regex)

        if isinstance(new_urls, str):
            new_urls = [new_urls]
        for link in new_urls:
            self.result_dict.setdefault(base_url(link), [])

    def get_result_from_response(self):
        # get new results from response html
        new_results_list = list(set(re.findall(self.regex,
                                               self.response, re.I)))
        if new_results_list:
            self.add_result(self.current_url)  # the result is the current url

    def add_result(self, result):
        """
        Add result link to result_dict.
        :param result: Link with key word match
        :return: None
        """
        result_from_rslt_dict = self.result_dict[self.get_current_base_url()]
        if result not in result_from_rslt_dict:
            result_from_rslt_dict.append(result)
