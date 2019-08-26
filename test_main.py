from scraper_class import Scraper

# url = Scraper('http://books.toscrape.com/')
input_url = input('What website would you like to scrape?\n: ').rstrip()
url = Scraper(input_url)
url.sleep_time = 0
url.scrape()
print(f'Urls Scraped: {url.get_total_urls_scraped()}')
