"""Download all files of n file type from a website"""
import os.path
import time
from urllib.parse import urlparse

import requests

from crawl import Crawl


class LinkFileType(Crawl):
    """Download all files of n file type from a website"""
    result_list = []

    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                       'AppleWebKit/537.36 (KHTML, like Gecko)'
                       'Chrome/76.0.3809.100 Safari/537.36')
    }

    def __init__(self, new_urls, file_type):
        super().__init__(new_urls)
        if isinstance(file_type, str):
            self.file_type = [file_type.strip()]
        elif isinstance(file_type, list):
            file_type = [i.strip() for i in file_type]
            self.file_type = file_type
        elif isinstance(file_type, str) and ',' in file_type:
            file_list = file_type.split(',')
            file_list = [i.strip() for i in file_list]
            self.file_type = file_list
        else:
            print('How did you mess this up?')

    def downloader(self):
        """
        Download the files from each url in result_list, ex. http://keygenmusic.net/?page=team&teamname=acme&lang=en
        :return: None
        """
        for file_num, url in enumerate(self.result_list):
            file_num += 1
            print(f'Downloading Files: {round((file_num/len(self.result_list))* 100)}%', end='\r')

            # get the file name
            path = urlparse(url).path
            path_split = os.path.split(path)
            file_name = path_split[-1]

            # check if the session folder name exists, create it if not
            dir_path = f'./downloads/{self.session_name}'
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)

            # download the file
            r = requests.get(url, stream=True)
            with open(f'{dir_path}/{file_name}', 'wb') as f:
                f.write(r.content)
        print('Downloading Complete', end='\r')
        print(f'Number of files downloaded: {len(self.result_list)}')

    def add_result(self):
        """
        Add the current url if the current url content-type is a match.
        :return: None
        """
        self.result_list.append(self.current_url)

    def check_file_type(self, response):
        # check file type
        content_type = response.headers['content-type']
        for file_type in self.file_type:
            if file_type in content_type or file_type in self.current_url:
                self.add_result()

    def set_response_with_html(self):
        url = self.current_url
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            # todo: add a way to check the content type and content length and then filter from with this function
            status_code = response.status_code

            # Don't set response if the content is above a certain size in bytes
            if len(response.content) >= 20_000_000:
                print('LargeFile: Avoiding')
                self.buggy_url_list.append(self.current_url)
                self.response = None

            elif response.history and status_code in range(200, 226):
                # if the response was redirected to a new url and 200 status code
                self.current_url = response.url
                self.response = response.text
                self.check_file_type(response)
                self.add_url_counter()

            elif status_code in range(200, 226):
                # if the response has a successful status code
                try:
                    self.response = response.text
                    self.check_file_type(response)
                    self.add_url_counter()
                except KeyError:
                    self.buggy_url_list.append(self.current_url)
                    self.response = None

            elif status_code in range(300, 511):
                # if the response was redirected, or had a client or server error
                self.buggy_url_list.append(self.current_url)
                self.response = None
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema,
                requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,
                requests.exceptions.Timeout, requests.exceptions.TooManyRedirects) as e:
            self.response = None

    def crawl(self):
        session = self.session_name
        try:
            while len(self.new_urls):
                self.set_current_url()
                queue = len(self.new_urls)
                processing = self.current_url
                status = 'crawling'
                # print(f'|Session:{session}|Status:{status}|Queue:{queue}|Processing:{processing}')
                print(f'|Session:{session}|Status:{status}|Queue:{queue}|Files Found: {len(self.result_list)}|Processing:{processing}', end='\r')
                self.set_response_with_html()
                if self.response:
                    self.get_new_urls_from_html()
                    time.sleep(self.sleep_time)
                # self.save_progress()
                time.sleep(.1)

            # crawl complete
            # self.save_progress()
            # print(f'Session - {self.session_name}')
            status = 'crawl complete'
            print(f'|Session:{session}|Status:{status}|')
            self.downloader()
            # self.print_buggy_links()
        except KeyboardInterrupt:
            self.print_buggy_links()
        return {'session_name': self.session_name,
                'url_counter': self.url_counter,
                'debug_dict': self.debug_dict}

