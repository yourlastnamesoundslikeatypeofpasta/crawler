def find_abs_path(link, rel_link):
    """
    Find the new_urls from a relative link that uses 'dots'. ex. '../../directory/index.html'
    :param link: The current new_urls where the relative link was found
            ex. 'http://books.toscrape.com/catalogue/category/books/travel_2/index.html'
    :param rel_link: A relative link that includes 'dots'. ex. '../../directory/index.html'
    :return:
    """
    link_list = link.split('/')
    del link_list[-1]  # remove the trailing .html file from the path
    rel_link_list = rel_link.split('/')
    new_link_list = []
    for dot_dot in rel_link_list:
        if dot_dot == '..':
            del link_list[-1]
            continue
        new_link_list.append(dot_dot)
    resolved_link = '/'.join(link_list) + '/' + '/'.join(new_link_list)

    # TESTING FOLLOWING CODE BLOCK
    # ADDING THE MIDDLE FOREWORD SLASH IF IT ISN'T THERE
    # resolved_link = '/'.join(link_list)
    # if not resolved_link.endswith('/'):
    #     resolved_link = resolved_link + '/'
    # resolved_link + '/'.join(new_link_list)
    # NOT WORKING!!

    return resolved_link
