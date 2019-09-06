"""A sub-class of ScrapeReg. Crawl through pages and return links that contain html that match the key/regex"""
import os
import re
import sys
import time
import tkinter
from tkinter import filedialog

import openpyxl

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

    @staticmethod
    def import_urls_from_excel():

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
            txt_path = filedialog.askopenfilename(parent=root, initialdir=curr_path,
                                                  title='Choose the excel sheet you want to import')
            return txt_path  #todo: test me on lunix box, getting weird error on mac box

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
