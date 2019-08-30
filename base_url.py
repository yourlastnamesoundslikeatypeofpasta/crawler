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

    # Add 'http://' if the new_urls is missing scheme
    if url.startswith('http://') is False and url.startswith('https://') is False:
        url = 'http://' + url

    # Split out the base new_urls from the new_urls
    parts = urlsplit(url)
    url_base = "{0.scheme}://{0.netloc}".format(parts)

    # Check if the base new_urls ends with a preferred extension domain and return the base new_urls
    while len(url_base) > 3:
        for ex in ext_lst:
            if url_base.endswith(ex):
                # Add a trailing foreword slash if the the link doesn't have one
                if url_base.endswith('/') is False:
                    url_base = url_base + '/'
                return url_base
        print(f'URL Extension: {url_base[-4:]} is not in extension list for {url_base}')
        # Add a trailing foreword slash if the the link doesn't have one
        if url_base.endswith('/') is False:
            url_base = url_base + '/'
        return url_base
