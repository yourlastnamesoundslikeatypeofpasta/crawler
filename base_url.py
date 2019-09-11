"""Take a raw URL and extract base URL"""
from urllib.parse import urlsplit


def base_url(url):
    """
    Take a raw URL and extract base URL
    :param url: Raw URL: http://google.com/q=dog%sprinting%on%treadmill
    :return: http://google.com
    """
    # Add 'http://' if the new_urls is missing scheme
    if url.startswith('http://') is False and url.startswith('https://') is False:
        url = 'http://' + url

    # Split out the base new_urls from the new_urls
    parts = urlsplit(url)
    url_base = f"{parts.scheme}://{parts.netloc}/"

    return url_base
