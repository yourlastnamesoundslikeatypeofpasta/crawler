import multiprocessing
import os

from crawl import Crawl
from link_key import LinkKey
from scrape_reg import ScrapeReg


def initiate_crawl(url):
    """Crawl a given url with multiprocessing"""
    return Crawl(url).crawl()


def resume_crawl(crawl_object):
    """
    Resume a crawl.
    :param crawl_object: The Crawl object
    :return: None
    """
    return crawl_object.crawl()


def initiate_scrape_reg(iterable):
    url_list = iterable[0]
    regex = iterable[-1]
    return ScrapeReg(url_list, regex).crawl()


def resume_scrape_reg(scrape_reg_object):
    pass


def initiate_link_key(iterable):
    url_list = iterable[0]
    regex = iterable[-1]
    result_tup = LinkKey(url_list, regex).crawl()
    return result_tup


def resume_link_key(url):
    pass


def main():

    def get_session_type():
        sesh_types = ['Scrape - Get Info <i>', 'Scrape - Get Links <l>']
        print('What type of session would you like to initiate?')
        print(f'\tTypes:')
        for sesh in sesh_types:
            print(f'\t\t{sesh}')

        while True:
            type_resp = input(': ').lower()
            if 'i' in type_resp:
                return ScrapeReg
            elif 'l' in type_resp:
                return LinkKey
            else:
                print('InvalidInput: Enter <i> or <l>')

    def multiprocess(func, iterable):
        """
        Initiate the multiprocess pool method.
        :param func: a reference to the function/method to be used
        :param iterable: an iterable of the variables to pass into the function
        :return: a list of outputs from the mapping func, iterable
        """
        def create_pool_size(session_list):
            """
            Create an appropriate pool size. If the length of domains exceeds the number of threads
            than the pool_size will be the max number of threads, else the pool size will be the
            number of domains entered.
            :param session_list:
            :return:
            """
            # multiprocess crawl threads
            list_count = len(session_list)
            thread_count = multiprocessing.cpu_count() * 2

            # create a pool size based on the size of session_list
            if list_count > thread_count:
                pool_size = thread_count
            else:
                pool_size = list_count
            return pool_size

        def print_pool_out(output_list):
            """
            Print the output of each crawl process from the output list
            :param output_list: a list that contains tuples (session_name, list_of_results)
            :return: None
            """
            for session_name, result_list in output_list:
                print(session_name)
                if result_list:
                    for link in result_list:
                        print(f'\t{link}')
                else:
                    print(f'\tNo Results Found')

        pool_size = create_pool_size(iterable)
        pool = multiprocessing.Pool(
            processes=pool_size
        )
        pool_outputs = pool.map(func, iterable)
        pool.close()
        pool.join()

        print(pool_outputs)
        print_pool_out(pool_outputs)

    def new_sesh():
        """
        Create a new crawl session, and then crawl.
        :return: None
        """

        def list_or_string(links):
            """
            Convert the input into a list. If the input has commas,
            convert it to a list.
            :param links: inputted url(s).
            :return: a list of urls or a list with one url
            """
            if ',' in links:
                links = links.split(',')
                links = [i.strip() for i in links]
                return links
            else:
                return [links.rstrip()]

        def create_scrape_reg():
            """
            Initiate scrape_reg
            :return: Output of scrape_reg.crawl()
            """
            url = input('Enter URL or a list of urls separated by a comma\n: ').lower()
            url_list = list_or_string(url)
            regex = input('Enter the Regular Expression of the info you would like to extract\n: ').lower()
            url_regex_tup = [(url, regex) for url in url_list]

            if len(url_list) == 1:
                return ScrapeReg(url, regex).crawl()
            return multiprocess(initiate_scrape_reg, url_regex_tup)

        def create_link_key():
            """
            Initiate link_key
            :return: Output of link_key.crawl()
            """
            url = input('Enter URL or a list of urls separated by a comma\n: ').lower()
            url_list = list_or_string(url)
            # todo: turn url_list into a set list, just in case the same url is added into the input list twice
            regex = input('Enter the Regular Expression of the info you would like to extract\n: ').lower()
            url_regex_tup = [(url, regex) for url in url_list]

            if len(url_list) == 1:
                return LinkKey(url.rstrip(), regex).crawl()
            return multiprocess(initiate_link_key, url_regex_tup)

        sesh_type = get_session_type()

        if sesh_type == ScrapeReg:
            create_scrape_reg()
        elif sesh_type == LinkKey:
            create_link_key()

    def resume_sesh():
        """
        List saved crawl sessions, and then resume crawl session.
        :return: None
        """

        def print_sesh_list(sesh_list):
            """
            Print the current session list.
            :param sesh_list: The current session list
            :return:
            """
            if not sesh_list:
                print('Resume Session List:\n\tCurrently Empty :(')
            else:
                print('Resume Session list:')
                for session in sesh_list:
                    print(f'\t{session}')

        def print_saved_sessions(file_list):
            """
            Print out the saved .db files in the ./save directory
            :param file_list: the list of file name to print out
            :return: None
            """
            print('Saved Sessions:')
            for file_name in file_list:
                print(f'\t{file_name}')

        def get_saved_sessions():
            """
            Get a list of the saved .db files in the ./save directory
            :return: A list of the name of the saved .db files
            """
            path = './save'
            dirs = os.listdir(path)
            printed_files_list = []
            for file in dirs:
                filename, file_extension = os.path.splitext(file)

                # the shelve module occasionally creates other files along with the .db
                if file_extension != '.db':
                    filename, file_extension = os.path.splitext(filename)

                if filename not in printed_files_list and file_extension == '.db':
                    printed_files_list.append(filename)
            return printed_files_list

        def create_crawl_objects(sesh_list):
            """
            Create crawl objects for each file_name in session list.
            :param sesh_list: list of sessions to create crawl objects
            :return: A list of crawl objects
            """
            return [Crawl.from_save(session) for session in sesh_list]

        def get_session_list():
            """
            Get a list of sessions that the user wishes to resume.
            :return: A list of session names
            """
            session_list = []
            printed_files_list = get_saved_sessions()
            while True:
                if not printed_files_list:
                    # if the user enters in all of the saved sessions
                    print(
                        'You have added all of the session saves to your resume list, press [ENTER] to initiate crawls.')
                    input(': ')
                    break
                print_saved_sessions(printed_files_list)
                print_sesh_list(session_list)
                session_name = input(': ')
                if session_name in printed_files_list:
                    session_list.append(session_name)
                    printed_files_list.remove(session_name)
                elif session_name in session_list:
                    print(f'{session_name} already in resume session list')
                elif session_name == 'q':
                    break
                else:
                    print(f'Session not found: {session_name}')
            if not session_list:
                return None
            else:
                return session_list

        sesh_type = get_session_type()

        print('|Enter the sessions you wish to resume|Enter [Q] to initiate crawl sessions')

        # get a list of session the user wishes to resume
        session_list = get_session_list()

        # if the user didn't add any session names to the Resume Session List
        if not session_list:
            return print('Sessions not added to Resume Session List')

        # create a list of crawl objects
        session_objects = create_crawl_objects(session_list)

        # if the user wishes to resume crawl of one list, don't use multiprocessing
        if len(session_list) == 1:
            crawl_object = session_objects[0]
            outputs = resume_crawl(crawl_object)
            return print(outputs)

        multiprocess(resume_crawl, session_objects)

    print('Welcome to Scraper!')

    # create the save directory if it doesn't exist
    path = './save/'
    if not os.path.exists(path):
        os.mkdir(path)

    try:
        while True:
            print('[NEW SESSION] or [RESUME SESSION] or [QUIT] [N/R/Q]')
            sesh_response = input(': ').lower()
            if 'n' in sesh_response:
                new_sesh()
            elif 'r' in sesh_response:
                resume_sesh()
            elif 'q' in sesh_response:
                print('quitting')
                break
            else:
                print('Invalid entry')
    except KeyboardInterrupt:
        print('quitting')


if __name__ == '__main__':
    main()
