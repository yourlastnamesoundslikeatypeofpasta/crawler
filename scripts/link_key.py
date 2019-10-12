"""A sub-class of ScrapeReg. Crawl through pages and return links that contain html that match the key/regex"""
import os
import re
import shelve
import tkinter
from tkinter import filedialog

import openpyxl

from scripts.base_url import base_url
from scripts.scrape_reg import ScrapeReg


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

    def save_progress(self):
        """
                Save the variables new_urls, response, current_url, poss_link,
                url_counter, queue_counter, url_cap, sleep_time, debug_dict,
                and buggy_url_list with shelve.
                :return: None
        """
        # verify that the directory: ./save/link_key exists, create it, if not
        path = './save/link_key/'
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
        with shelve.open(f'./save/link_key/{name_session}.db', flag="r") as save:
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

    @staticmethod
    def import_urls_from_excel():

        def get_file_path():
            """
            Open a file dialog window and ask the user where their excel file
            is located.
            :return: a string of the absolute file path
            """
            # fixme: find MacOs solution. Dialog window hangs when file is selected.
            # Set up the tkinter object
            root = tkinter.Tk()
            root.withdraw()

            # Bring up the dialog window
            curr_path = os.getcwd()
            txt_path = filedialog.askopenfilename(parent=root, initialdir=curr_path,
                                                  title='Choose the excel sheet you want to import')
            return txt_path

        # path = '/Users/ChristianZagazeta/Downloads/florida_cities_a_c_2007_2012.xlsx'
        path = get_file_path()
        wb = openpyxl.load_workbook(path)
        try:
            sheet = wb.active
            column_3_rows = len(sheet['E'])
            websites = []
            for row in range(1, column_3_rows):
                cell = sheet.cell(row=row, column=5).value
                if isinstance(cell, str):
                    if cell.startswith('http') or cell.startswith('www'):
                        websites.append(cell)
            return websites
        except BaseException as e:
            print(f'Error:{e}')
            wb.close()
