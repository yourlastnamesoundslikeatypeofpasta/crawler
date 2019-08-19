"""Take a raw URL and extract base URL"""
from urllib.parse import urlsplit


def base_url(url):
    """
    Take a raw URL and extract base URL
    :param url: Raw URL: http://google.com/q=dog%sprinting%on%treadmill
    :return: http://google.com
    """
    # List of preferred domains the URL should end with.
    ext_lst = ['org', 'com', 'edu', 'net', 'gov', '.us',

               '.mx', 'mil', '.ca', 'business.site', 'nfo',
               'health', 'biz', '.br', '.life', '.au']

    # Add 'http://' if the url is missing scheme
    if url.startswith('http://') is False and url.startswith('https://') is False:
        url = 'http://' + url

    # Split out the base url from the url
    parts = urlsplit(url)
    url_base = "{0.scheme}://{0.netloc}".format(parts)

    # Check if the base url ends with a preferred extension domain and return the base url
    while len(url_base) > 3:
        for ex in ext_lst:
            if url_base.endswith(ex):
                return url_base
        print(f'URL Extension: {url_base[:-3]} is not in extension list.')
        return url_base
