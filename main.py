"""This script crawls through a website, and scrapes each url for an e-mail address"""
import re
import sys
import time
from collections import deque
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup

from base_url import base_url


def main():
    """
    Main func.
    :return: A list of e-mails scraped from the input website.
    """
    # request_url = input('What is the URL you would like to scrape?\n: ')
    new_urls = deque(['https://www.smh.com.au/contact-us'])
    processed_urls = []
    url_cap = 1500
    exclude_ext = ['image', 'pdf', 'jpg', 'png', 'gif', 'xlsx', 'spx',
                   'mp3', 'csv', 'wma', 'provider', 'specialtie', 'pptx',
                   'asp', 'mp4', 'download', 'javascript', 'tel:', 'pdf']

    if not bool(new_urls):
        sys.exit()

    email_dict = {}
    url_counter = {}
    queue_counter = {}

    while len(new_urls):
        # grab the new url from new_urls and add it to the processed urls list
        url = new_urls.popleft()
        processed_urls.append(url)

        # extract base url to resolve relative link
        url_base = base_url(url)
        parts = urlsplit(url)
        if parts.scheme != 'mailto' and parts.scheme != '#':
            path = url[:url.rfind('/') + 1] if '/' in parts.path else url
        else:
            continue

        # Increment the url cap + 1
        url_counter.setdefault(url_base, 0)
        url_counter[url_base] += 1

        # Check if the url cap limit has been reached
        if url_counter[url_base] >= url_cap:
            # insert function to remove websites with this url_base from the queue
            continue

        # get url's HTML
        print(f"Processing {url}", file=sys.stderr)
        # try to get html for url
        try:
            response = requests.get(url, timeout=10).text  # timeout if no response within 10 seconds
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema,
                requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,
                requests.exceptions.Timeout, requests.exceptions.TooManyRedirects) as e:
            # ignore pages with errors/timeout
            print(f'ERROR {e}: Link Skipped!')
            continue

        # extract all email addresses from response.text and append them to new_emails
        new_emails = list(set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response, re.I)))
        # checks if new emails are in the captured emails list, remove the duplicates from new_emails
        if new_emails:
            new_emails = [i.lower() for i in new_emails]
            try:
                captured_url_emails = email_dict[base_url(url)]
                if new_emails:
                    for email in new_emails:
                        if email in captured_url_emails:
                            new_emails.remove(email)
            except KeyError:
                for email_list in email_dict.values():
                    for e_mail in email_list:
                        if e_mail in new_emails:
                            new_emails.remove(e_mail)

            # add a dictionary to email_list
            try:
                email_list = email_dict[url_base]
                for email in new_emails:
                    email_list.append(email)
            except KeyError:
                email_dict.setdefault(url_base, new_emails)

        # create a beautiful soup for the html document, and then grab
        soup = BeautifulSoup(response, features="html.parser")

        # Only queue up to 1500 links for each base url
        queue_counter.setdefault(url_base, 1)

        # find and process all the anchors in the document
        for anchor in soup.find_all("a"):

            # Checks to see if url_count + what was added in queue will be over the urlcap limit
            if queue_counter[url_base] >= url_cap:
                print(f'Queue Capped: {url_base}: {queue_counter[url_base]}')
                break

            # extract link url from the anchor
            try:
                if 'href' in anchor.attrs or anchor.attrs['href'].find('mailto') == -1:
                    link = anchor.attrs["href"]
            except KeyError:
                print(f'Error: KeyError, Link: {url}')

            # resolve relative links
            if link.startswith('/'):
                link = url_base + link
            elif not link.startswith('http'):
                link = path + link

            # skips over links with the following words in the link
            exclude_bool = False
            for extension in exclude_ext:
                if extension in link:
                    exclude_bool = True
                    break
            if exclude_bool:
                continue

            # add the new url to the queue if it was not enqueued nor processed yet
            if (url_base in link) and (link not in processed_urls):
                new_urls.append(link)
                print(f'New URL Added: {link}')
                queue_counter[url_base] += 1

        # print out found email
        for url, email_list in email_dict.items():
            print(url, email_list)

        # print out how many urls the base url has left to scan
        print(queue_counter[url_base] - len(processed_urls), f'in queue for {url_base}')

        # print out how many urls are left to scan
        print(len(new_urls), 'to scan')
        time.sleep(5)


if __name__ == '__main__':
    main()
