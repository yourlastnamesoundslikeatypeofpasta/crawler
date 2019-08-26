from scraper_class import Scraper

# url = Scraper('http://books.toscrape.com/')
input_url = input('What website would you like to scrape?\n: ').rstrip()
url = Scraper(input_url)
url.sleep_time = 0
url.scrape()
urls_scraped = [i for i in url.url_counter.values()][0]
print(f'Urls Scraped: {urls_scraped}')
print(f'Urls Scraped: {len(url.processed_urls)}')
