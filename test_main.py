from scraper_class import Scraper

print('Welcome to Scraper!')
from_string_or_list = input('Would you like to scrape a list of urls or one url? [l\\s]\n: ').lower()
if from_string_or_list == 'l':
    url_list = input('Enter your urls separated with a comma\n: ')
    input_url = url_list.split(',')
    input_url = [i.strip() for i in input_url]
else:
    input_url = input('Enter your url\n: ')
url = Scraper(input_url)
url.sleep_time = 2
url.scrape()
