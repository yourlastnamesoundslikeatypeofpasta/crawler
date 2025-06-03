import re
import requests
from collections import deque
from scripts.base_url import base_url

class Scraper:
    def __init__(self, url):
        self.new_urls = deque([url])
        self.email_dict = {}
        self.url_counter = {}
        self.queue_counter = {}
        self.current_url = None
        self.response = None

    def set_current_url(self):
        self.current_url = self.new_urls.popleft()
        base = self.get_current_base_url()
        self.email_dict.setdefault(base, [])
        self.url_counter.setdefault(base, 0)
        self.queue_counter.setdefault(base, 0)

    def get_current_base_url(self):
        return base_url(self.current_url)

    def set_response_with_html(self):
        r = requests.get(self.current_url, timeout=5)
        self.response = r.text

    def get_email_from_response(self):
        if not self.response:
            return
        new_emails = list(set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", self.response, re.I)))
        if new_emails:
            base = self.get_current_base_url()
            self.email_dict[base].extend(new_emails)

    def print_emails(self):
        for base, emails in self.email_dict.items():
            print(base, emails)
