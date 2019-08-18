from collections import deque
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import parts as parts
import base_url
import sys
import requests
import re
import os

print(os.getcwd())

test = base_url.base_url('https://www.smh.com.au/contact-us')
print(test)
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
process_count = 0

print(f'Working {new_urls[0]}')
while len(new_urls):
    # grab the new url from new_urls and add it to the processed urls list
    url = new_urls.popleft()
    processed_urls.append(url)

    # extract base url to resolve relative link
    url_base = base_url(url)
    print('Test line passed')

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
    print(f"Processing {url}")
    # try to get html for url
    try:
        response = requests.get(url, timeout=10).text  # timeout if no response within 10 seconds
    except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema, requests.exceptions.ConnectionError,
            requests.exceptions.InvalidURL, requests.exceptions.Timeout, requests.exceptions.TooManyRedirects) as e:
        # ignore pages with errors/timeout
        print(f'ERROR {e}: Link Skipped!')
        continue

    # extract all email addresses from response.text and append them to new_emails
    new_emails = list(set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response, re.I)))
    print(new_emails)
    # checks if new emails are in the captured emails list, remove the duplicates from new_emails
    if new_emails:
        new_emails = [i.lower() for i in new_emails]
        try:
            captured_url_emails = email_dict[url_base(url)]
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
    soup = BeautifulSoup(response.text, features="html.parser")

    # QueueCount counts how many new urls will be added to the queue list for base URL
    queue_count = 0

    # queueCounter[url_base] will default to the remaining balance of
    queue_counter.setdefault(url_base, queue_counter[url_base])

    # find and process all the anchors in the document
    for anchor in soup.find_all("a"):
        # Checks to see if urlcount + what was added in queue will be over the urlcap limit
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

        # skips over links with the following extensions
        for extension in exclude_ext:
            if extension in link:
                continue

        # add the new url to the queue if it was not enqueued nor processed yet
        if (link not in new_urls) and (url_base in link) and (link not in processed_urls):
            new_urls.append(link)
            print(f'New URL Added: {link}')
            queue_counter += 1
    queue_counter[url_base] += queue_count









'''
# Create a list of processed Urls
        processedUrls = processUrls(wb, 3)

        # Create a dictionary that has a key of how many times a
        # base url was scraped
        urlCounter = urlScanCount(wb)
        queueCounter = {}

        # Create a deque of new urls to crawl
        urlCap = 1500
        excludeExt = ['image', 'pdf', 'jpg', 'png', 'gif', 'xlsx', 'spx', 'mp3', 'csv', 'wma', 'provider', 'specialtie',
                      'pptx', 'asp', 'mp4', 'download']
        new_urls = newUrls(sheet, processedUrls, urlCounter, excludeExt, urlCap)

        # If no new urls to scrape end webScrape()
        if bool(new_urls) == False:
            wb.close(

        # A list of crawled emails
        emails = []

        # Amount of links that have been processed during the session
        processedCount = 0
        # begin web scraping
        while len(new_urls):
            # For every 200 processed urls, save worksheet
            if processedCount % 200 == 0 and processedCount > 0:
                # Save spreadsheet
                colorPrint('CYAN', 'saving spreadsheet...')
                wb.save("C:/Users/chris/Google Drive/cities-and-towns-of-the-united-states.xlsx")
                colorPrint('GREEN', 'saved!')
                # reconfigure rows
                sheet = wb['Sheet2']
                processedRow = findRow(sheet, 3)
                newUrlRow = findRow(sheet, 2)
            # sheet = wb['Sheet3']
            # urlRow = findRow(sheet, 2)
            # emailRow = findRow(sheet, 3)
            # Reset processedUrls
            # processedUrls = []
            gooWebsiteRow = findRow(gooSheet, 2)
            gooEmailRow = findRow(gooSheet, 3)
            time.sleep(random.uniform(0, timeAns))
            sheet = wb['Sheet2']

            #  process urls one by one until we exhaust the queue
            url = new_urls.popleft()
            processedUrls.append(url)
            sheet.cell(row=processedRow, column=3).value = url
            processedRow += 1
            processedCount += 1
            # extract base url to resolve relative links
            parts = urlsplit(url)
            base_url = "{0.scheme}://{0.netloc}".format(parts)
            if parts.scheme != 'mailto' and parts.scheme != '#':
                path = url[:url.rfind('/') + 1] if '/' in parts.path else url
            else:
                continue

            # caps the amount of links to scrape from base_url to 1500
            urlCounter.setdefault(base_url, 0)
            urlCounter[base_url] += 1
            colorPrint('GREEN', f'Url Count: {urlCounter[base_url]}')
            # urlCap = 1500
            if urlCounter[base_url] >= urlCap:
                colorPrint('RED', f'Capped Out: {base_url} @ {urlCounter[base_url]}')
                # insert function to remove websites with this base_url from the queue
                continue
            # get url's content
            colorPrint('MAGENTA', f"Processing {url}")
            # try to get html for url
            try:
                response = requests.get(url, timeout=10)  # timeout if no response within 10 seconds
            # print(len(response))
            # except (requests.exceptions.MissingSchema,requests.exceptions.InvalidSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.Timeout, requests.exceptions.TooManyRedirects):
            except:
                # ignore pages with errors/timeout
                stats(emails, new_urls, processedCount)
                colorPrint('RED', 'Error- Skipping Link')
                continue
            # extract all email addresses and add them into the resulting set
            new_emails = list(set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I)))
            if new_emails != []:  # if email not found
                new_emails = [i.lower() for i in new_emails]
                emailDuplicate = False
                # checks if email captured is in current capture list
                for email in emails:
                    for value in email['emails']:
                        if value in new_emails:
                            emailDuplicate = True
                # checks if email captured is in email database
                for e in new_emails:
                    if emailCheck(e, wb) or emailCheck1(e, gooWb) or emailCheck2(e, wb):
                        emailDuplicate = True
                if emailDuplicate == True:  # if email is in email list dont write to spreadsheet
                    colorPrint('RED', 'Duplicate Email Avoided!')
                    stats(emails, new_urls, processedCount)
                    continue
                new_emails = list(set(new_emails))
                # write email/date to google spreadsheet
                dateNow = date.today().__format__('%m/%d/%y').strip('0')
                gooSheet.cell(row=gooWebsiteRow, column=2).value = base_url
                gooSheet.cell(row=gooEmailRow, column=3).value = '\n'.join(new_emails)
                gooSheet.cell(row=gooEmailRow, column=4).value = dateNow
                last_update = f'Last Update: {dateNow}'
                # uodate date if needed
                date_cell = gooSheet.cell(row=3, column=6).value
                if date_cell != last_update:
                    gooSheet.cell(row=3, column=6).value = last_update
                # update email count and save
                email_count = emailCount(gooWb)
                t_email_found = f'Total Emails Found: {email_count}'
                gooSheet.cell(row=6, column=6).value = t_email_found
                gooWb.save("C:/Users/Chris/Google Drive/live_email_list.xlsx")
                # write emails to main spreadsheet and save to dictionary 'emails'
                # sheet = wb['Sheet3']
                # sheet.cell(row= urlRow, column= 2).value = base_url
                # urlRow += 1
                # sheet.cell(row= emailRow, column= 3).value = '\n'.join(new_emails)
                # emailRow += 1
                emails.append({'url': url, 'emails': new_emails})
            # create a beutiful soup for the html document
            try:
                soup = BeautifulSoup(response.text, features="html.parser")
            except:
                colorPrint('RED', 'ERROR: Link Error')
                continue
            # QueueCount counts how many new urls will be added to the queue list for base URL
            queueCount = 0
            # queueCounter[base_url] will default to the remaining balance of
            queueCounter.setdefault(base_url, urlCounter[base_url])
            # find and process all the anchors in the document
            for anchor in soup.find_all("a"):
                # Checks to see if urlcount + what was added in queue will be over the urlcap limit
                if queueCounter[base_url] >= urlCap:
                    # colorPrint('RED', f'Queue Capped: {base_url}: {queueCounter[base_url]}')
                    break
                # extract link url from the anchor
                try:
                    if 'href' in anchor.attrs or anchor.attrs['href'].find('mailto') == -1:
                        link = anchor.attrs["href"]
                except KeyError:
                    # colorPrint('RED', 'Error: KeyError')
                    pass

                # resolve relative links
                if link.startswith('/'):
                    link = base_url + link
                elif not link.startswith('http'):
                    link = path + link

                # skips over links with the following extensions
                if link[
                   -3:].lower() in excludeExt or 'javascript' in link or 'tel:' in link or '.xlsx' in link or '.pdf' in link:
                    continue
                # add the new url to the queue if it was not enqueued nor processed yet
                if (link not in new_urls) and (base_url in link) and (link not in processedUrls):
                    sheet = wb['Sheet2']
                    try:
                        sheet.cell(row=newUrlRow, column=2).value = link
                    except openpyxl.utils.exceptions.IllegalCharacterError:
                        continue
                    new_urls.append(link)
                    print(f'New URL Added: {link}')
                    newUrlRow += 1
                    queueCount += 1
            queueCounter[base_url] += queueCount
            stats(emails, new_urls, processedCount)
        saveWorkbook(wb)
        gooWb.close()
        colorPrint('GREEN', f'Output: {emails}')
    except BaseException as e:
        print(f'Failed to do something: {e}')
        # print('Error - Scrape Error')
        destroy(wb)
        destroy(gooWb)
        # print(xlsx)
        textMe('+19414836745', f'Scrape Error: {e}')
        
        '''