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

    # ask the user the website they would like to scrape
    request_url = input('What is the URL you would like to scrape?\n: ').rstrip()
    # request_url = 'https://www.smh.com.au/contact-us'
    new_urls = deque([request_url])

    # exit the program if the user didn't enter in a url
    if not bool(new_urls):
        sys.exit()

    exclude_ext = ['image', 'pdf', 'jpg', 'png', 'gif', 'xlsx', 'spx',
                   'mp3', 'csv', 'wma', 'provider', 'specialtie', 'pptx',
                   'asp', 'mp4', 'download', 'javascript', 'tel:', 'pdf',
                   'specialty']
    email_dict = {}
    url_counter = {}
    queue_counter = {}
    processed_urls = []
    url_cap = 1500

    while len(new_urls):
        # grab the new url from new_urls and add it to the processed urls list
        url = new_urls.popleft()
        processed_urls.append(url)
        url_base = base_url(url)

        # extract url to resolve relative link
        parts = urlsplit(url)
        print(parts)
        if parts.scheme != 'mailto' and parts.scheme != '#': # this code block may unnecessary
            # if '/' in parts.path:
            #     path = url[:url.rfind('/') + 1]
            #     print(f'Line 50: {path}', file=sys.stderr)
            # else:
            #     path = url
            #     print(f'Line 53: {path}', file=sys.stderr)
            path = url[:url.rfind('/') + 1] if '/' in parts.path else url
        else:
            print('Continuing')
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

        # FIXME: Formulate a regex that will find 404 errors
        #   print out if page throws a 404 error
        # four_oh_four_re = re.compile(r'404')
        # four_oh_four_mo = four_oh_four_re.findall(response)
        # if four_oh_four_mo:
        #     print(f'ERROR: 404!', file=sys.stderr)
        #     print(response, file=sys.stderr)
        #     continue

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
                else:
                    print(f'line 134: Link: {anchor} didnt have href, WARNING')
            except KeyError:
                print(f'Error: KeyError, Link: {url}', file=sys.stderr)
                continue

            # resolve relative links
            if link.startswith('/'):
                link = path + link # testing this line
                # link = url_base + link

            # check link for criteria
            exclude_bool = False
            for extension in exclude_ext:
                # skips over links with the following keywords from exclude_ext
                if extension in link:
                    exclude_bool = True
                    print(f'Extension: {extension} in {link}')
                    break
            if exclude_bool:
                print(f'Excluded text found in link')
                continue
            elif link in processed_urls:
                print(f'Link: {link} in processed urls.')
                continue
            elif link in new_urls:
                print(f'Link: {link} in new urls')
                continue
            elif link.startswith('mailto:'):
                # Slice 'mailto:' from link and add the email to the email list if it isn't in the list
                email_from_link = link[7:]
                try:
                    email_list = email_dict[url_base]
                    if email_from_link not in email_list:
                        email_list.append(email_from_link)
                except KeyError:
                    email_dict.setdefault(url_base, [email_from_link])
                    continue
            elif url_base not in link:
                print(f'Link: {link} doesnt have url base {url_base}')
                continue
            else:
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
