"""Download all files of n file type from a website"""
import os
import re
import requests
import shelve
import sys
import time

from crawl import Crawl


class LinkFileType(Crawl):
    """Download all files of n file type from a website"""
    # todo: create a result list with all of the links with successful matches and then
    #   when the crawl is finished go through each link and download and store each file
    def __init__(self, new_urls, file_type):
        super().__init__(new_urls)

        # check if the file type is valid
        with open('./resources/content_types.txt', 'r') as types:
            type_list = types.readlines()
            type_list = [i.rstrip() for i in type_list]
            if file_type in type_list:
                self.file_type = file_type
            else:
                print(f'FileTypeError: {file_type} is not a valid file type')
                return

    def set_response_with_html(self):
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
                self.buggy_url_list.append(self.current_url)
                self.response = None
            elif response.history and status_code in range(200, 226):
                # if the response was redirected to a new url and 200 status code
                self.current_url = response.url
                self.response = response.text
                self.add_url_counter()
            elif status_code in range(200, 226):
                # if the response has a successful status code
                try:
                    self.response = response.text
                    self.add_url_counter()
                except KeyError:
                    self.buggy_url_list.append(self.current_url)
                    self.response = None
            elif status_code in range(300, 511):
                # if the response was redirected, or had a client or server error
                self.buggy_url_list.append(self.current_url)
                self.response = None

            # if status_code != 200:
            #     # Add the current new_urls and new link to the the debug dictionary and print out the status code
            #     # print(f'Status Code Error: {self.current_url}: {status_code}', file=sys.stderr)
            #     self.buggy_url_list.append(self.current_url)
            #     self.response = None
            # else:
            #     try:
            #         self.response = response.text
            #         self.add_url_counter()
            #     except KeyError:
            #         self.buggy_url_list.append(self.current_url)
            #         self.response = None
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema,
                requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,
                requests.exceptions.Timeout, requests.exceptions.TooManyRedirects) as e:
            # print(f'Link Error: {e}')
            self.response = None
            # pass
