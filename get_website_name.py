from urllib.parse import urlsplit


def get_web_name(url):
    """
    Get the name of a website.
    :param url: the url to get the name from
    :return: a string of the name of the website
    """
    parts = urlsplit(url)
    name_list = '{0.netloc}'.format(parts).split('.')
    web_name = ''

    # allow this function to create names that have multiple '.' or 'www' in them
    for name in name_list:
        if name.startswith('www') or name.startswith('com'):
            continue
        if web_name:
            web_name = web_name + '.' + name
        else:
            web_name = name
    return web_name
