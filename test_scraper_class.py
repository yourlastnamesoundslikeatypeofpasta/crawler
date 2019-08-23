import unittest
from collections import deque
from scraper_class import Scraper


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)

    def test_new_urls(self):
        url = Scraper('https://cannabistheorys.com/cannabis-theorys-muv-product-tutorial-11-thc-cbd-inhaler/')
        self.assertEqual(
            url.new_urls,
            deque(['https://cannabistheorys.com/cannabis-theorys-muv-product-tutorial-11-thc-cbd-inhaler/'])
        )

    def test_init_dictionaries(self):
        url = Scraper('https://cannabistheorys.com/cannabis-theorys-muv-product-tutorial-11-thc-cbd-inhaler/')
        self.assertEqual(len(url.email_dict), 1)
        self.assertEqual(len(url.url_counter), 1)
        self.assertEqual(len(url.queue_counter), 1)

    @ staticmethod
    def test_print_emails():
        url = Scraper('https://cannabistheorys.com/cannabis-theorys-muv-product-tutorial-11-thc-cbd-inhaler/')
        url.set_current_url()
        url.email_dict[url.get_current_base_url()] = ['chris@cb.com', 'beth@cb.com']
        url.email_dict.setdefault('bethsblueberrypies.com', ['beth@pie.com', 'chris@pie.com'])
        url.print_emails()


if __name__ == '__main__':
    # unittest.main()
    MyTestCase.test_print_emails
