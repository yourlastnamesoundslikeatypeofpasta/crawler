from urllib.parse import urlsplit


def get_web_name(url):
    parts = urlsplit(url)
    network_location = '{0.netloc}'.format(parts).split('.')[0]
    return network_location
