"""Download all files of n file type from a website"""
import os.path
import shelve
import time
from urllib.parse import urlparse
from sys import stdout

import requests

from scripts.crawl import Crawl


class LinkFileType(Crawl):
    """Download all files of n file type from a website"""
    result_list = []

    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                       'AppleWebKit/537.36 (KHTML, like Gecko)'
                       'Chrome/76.0.3809.100 Safari/537.36')
    }

    attribute_key_list = [
        'session_name',
        'result_list',
        'headers',
        'response',
        'current_url',
        'poss_link',
        'url_counter',
        'queue_counter',
        'url_cap',
        'queue_counter',
        'url_cap',
        'sleep_time',
        'debug_dict',
        'buggy_url_list'
    ]

    def __init__(self, new_urls, file_type):
        """
        Init.
        :param new_urls: list[url, url_1]
        :param file_type: dict['.extenstion': 'mimetype']
        """
        super().__init__(new_urls)
        self.file_type = file_type
        self.ext_list = [ext for ext in file_type.keys()]
        self.mime_list = [m_type for m_type in file_type.values()]

    def downloader(self):
        """
        Download the files from each url in result_list, ex. http://keygenmusic.net/?page=team&teamname=acme&lang=en
        :return: None
        """
        if self.result_list:
            # print out found files of each file type
            print('Files Found Breakdown:')
            for ext in self.ext_list:
                print(f'\t{ext}:')
                match_list = []
                for url in self.result_list:
                    if ext in url:
                        match_list.append(url)
                if match_list:
                    for match in match_list:
                        print(f'\t\t-> {match}')
                else:
                    print('\t\t-> No files found.')

            # ask the user if they would like to download the found files
            download_q = input(f'Download All Found Files: {len(self.result_list)} <yes|no>: ').lower()

            # create downloads folder if it doesn't exist
            path = './downloads'
            if not os.path.exists(path):
                os.mkdir(path)

            # download files
            if 'y' in download_q:
                print(f'Downloading {len(self.result_list)} files...')

                # check if the session folder name exists, create it if not
                dir_path = f'./downloads/{self.session_name}'
                if not os.path.exists(dir_path):
                    os.mkdir(dir_path)

                # download files from result_list
                for file_num, url in enumerate(self.result_list):
                    file_num += 1
                    print(f'Downloading File: {file_num} of {len(self.result_list)}|Completion: {round((file_num / len(self.result_list)) * 100)}%', end='\r')

                    # get the file name
                    path = urlparse(url).path
                    path_split = os.path.split(path)
                    file_name = path_split[-1]

                    # download the file
                    r = requests.get(url, stream=True)
                    try:
                        with open(f'{dir_path}/{file_name}', 'wb') as f:
                            f.write(r.content)
                    except PermissionError:
                        print('Permission Error: Try running as root...quitting...')
                        return

                # delete each entry from new_urls
                while self.new_urls:
                    self.new_urls.popleft()

                print('Downloads Complete', end='\r')
                print(f'Downloads Completed|Number of files downloaded: {len(self.result_list)}')
            else:
                print(f'Download Aborted.')
        else:
            print('No Files Found.')

    def add_result(self):
        """
        Add the current url if the current url content-type is a match.
        :return: None
        """
        if self.current_url not in self.result_list:
            self.result_list.append(self.current_url)

    def quick_squeeze(self):
        """
        Go through the new_urls list and check if any of the file types provided are in the url.
        This method isn't 100% accurate as some file types aren't included in the url so this method is intended
        to be used as a cast net.
        :return: None
        """
        print('\nLooking for files in queue list...')
        found_list = []
        found_count = 0
        # for each file_type, check if the file_type is in any of the urls in new_urls
        for file_type in self.ext_list:
            for url in self.new_urls:
                if (file_type in url) and (url not in self.result_list) and (url not in found_list):
                    found_count += 1
                    found_list.append(url)

        # check if each url has the correct content-type
        if found_count:
            print(f'confirming {found_count} files...this may take awhile...')
        else:
            return

        confirm_count = 0
        remove_list = []
        for url in found_list:
            content_type = requests.get(url).headers['content-type']
            for m_type in self.mime_list:
                if m_type in content_type:
                    self.result_list.append(url)
                    confirm_count += 1
                else:
                    if url in remove_list:
                        continue
                    remove_list.append(url)
            stdout.write(f'Confirmed: {confirm_count}/{found_count}\r')
            stdout.flush()

        # remove objects that weren't confirmed from found_list
        for url in remove_list:
            try:
                found_list.remove(url)
            except ValueError:
                # was throwing a ValueError, most likely multiple entries in remove_list
                continue

        # remove squeezed urls from new_urls
        for url in found_list:
            self.new_urls.remove(url)

    def check_file_type(self, response):
        # check file type
        content_type = response.headers['content-type']

        for m_type in self.mime_list:
            if m_type == content_type:
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

    def save_progress(self):
        """
        Save the variables new_urls, response, current_url, poss_link,
        url_counter, queue_counter, url_cap, sleep_time, debug_dict,
        and buggy_url_list with shelve.
        :return: None
        """
        # create the directory if it doesn't exit
        directory_path = './save/link_filetype'
        if not os.path.exists(directory_path):
            os.mkdir('save')
            os.mkdir(directory_path)

        # create a buffer dict
        buffer_save = {'new_urls': self.new_urls, 'file_type': self.file_type}
        for attribute in self.attribute_key_list:
            buffer_save[attribute] = getattr(self, attribute)

        # save buffer dict to shelve db
        with shelve.open(f'{directory_path}/{self.session_name}') as save:
            save['main'] = buffer_save

    @classmethod
    def from_save(cls, name_session):
        # create a dead dict with attribute_key_list, key: None
        attribute_dict = {key: None for key in cls.attribute_key_list}

        # give the dead dict some life from the shelve db
        with shelve.open(f'./save/link_filetype/{name_session}', flag="r") as save:
            save_dict = save['main']

            # directly grab the arguments needed to create an object
            new_urls = save_dict.get('new_urls')
            file_type = save_dict.get('file_type')

            # add attribute to the dead dict
            for attribute, v in save_dict.items():
                attribute_dict[attribute] = v

        # create an object to return
        url = LinkFileType(new_urls, file_type)
        for k, v in attribute_dict.items():
            setattr(url, k, v)
        return url

    def crawl(self):
        session = self.session_name
        status = 'CRAWLING...'
        try:
            # begin crawling
            squeeze_count = 0
            while self.new_urls:
                if not (squeeze_count % 500) and squeeze_count:
                    print('\nSqueezing...')
                    self.quick_squeeze()
                self.set_current_url()

                # print out stats
                queue = len(self.new_urls)
                # processing = self.current_url
                scanned = len(self.processed_urls)
                file_found = len(self.result_list)
                p = f'|Session:{session}|Status:{status}|Scanned:{scanned}|Queue:{queue}|Files Found:{file_found}|\r'
                stdout.write(p)
                stdout.flush()
                self.set_response_with_html()
                if self.response:
                    self.get_new_urls_from_html()
                    time.sleep(self.sleep_time)
                self.save_progress()
                # time.sleep(.1)
                squeeze_count += 1

            # crawl complete
            self.save_progress()
            status = 'crawl complete'
            print('')
            print(f'|Session:{session}|Status:{status}|')
            self.downloader()
            self.save_progress()
            # self.print_buggy_links()
        except KeyboardInterrupt:
            # perform a quick squeeze
            self.quick_squeeze()
            self.save_progress()

            # download files
            self.downloader()
            self.save_progress()

            self.print_buggy_links()
        return {'session_name': self.session_name,
                'url_counter': self.url_counter,
                'debug_dict': self.debug_dict}
