"""NOTE: RUN ME AS ADMIN/SUDO! Scrape a list of urls with multiprocessing in parallel."""
import multiprocessing
from crawl import Crawl


def crawl(url):
    """Crawl a given url with multiprocessing"""
    Crawl(url).crawl()


def main():
    url_list = ['https://pymotw.com/3/multiprocessing/communication.html#process-pools',
                'https://cannabistheorys.com/']
    pool_size = len(url_list)
    pool = multiprocessing.Pool(
        processes=pool_size
    )
    pool_outputs = pool.map(crawl, url_list)
    pool.close()
    pool.join()
    print(pool_outputs)


if __name__ == '__main__':
    main()
