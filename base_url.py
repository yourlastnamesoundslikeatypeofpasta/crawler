from urllib.parse import urlsplit


def base_url(url):
    """
    Take raw URL and extract base URL
    :param url: Raw URL: http://google.com/q=dog%sprinting%on%treadmill
    :return: http://google.com
    """

    ext_lst = ['org', 'com', 'edu', 'net', 'gov', '.us',

               '.mx', 'mil', '.ca', 'business.site', 'nfo',
               'health', 'biz', '.br', '.life', '.au']
    if url[:3] != 'http': # FIXME: function is returning: http://https:
                        #       and then going in an infinite loop in the proceeding while loop
        url = 'http://' + url
    parts = urlsplit(url)
    url_base = "{0.scheme}://{0.netloc}".format(parts)
    print(url_base)
    while len(url_base) > 3:
        for ex in ext_lst:
            if url_base.endswith(ex):
                return url_base

        # base_url_list = []
        # for char in base_url[::-1]:
        #     base_url_list.append(char)
        # url_base = ''.join(base_url_list)
    return url_base

print(base_url('https://www.smh.com.au/contact-us'))