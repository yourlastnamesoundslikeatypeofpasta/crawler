import multiprocessing
import mimetypes
import os
import sys

from scripts.crawl import Crawl
from scripts.link_key import LinkKey
from scripts.scrape_reg import ScrapeReg
from scripts.link_filetype import LinkFileType


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
    """
    Use ScrapeReg with the crawl method.
    :param iterable: a tuple, (url_list, regex)
    :return: a tuple that contains the session name and a list of results
    """
    url_list, regex = iterable
    return ScrapeReg(url_list, regex).crawl()


def resume_scrape_reg(scrape_reg_object):
    pass


def initiate_link_key(iterable):
    """
    Use LinkKey with the crawl method.
    :param iterable: a tuple, (url_list, regex)
    :return: a tuple that contains the session name and a list of results
    """
    url_list, regex = iterable
    result_tup = LinkKey(url_list, regex).crawl()
    return result_tup


def resume_link_key(url):
    pass


def initiate_link_file_type(iterable):
    """
    Use the LinkFileType class in conjunction with the crawl method.
    :param iterable: a tuple, (url_list, file_dict)
    :return: a tuple containing the session name and a list of results
    """
    url_list, file_dict = iterable
    result_tup = LinkFileType(url_list, file_dict).crawl()
    return result_tup


def resume_link_file_type(crawl_object):
    return crawl_object.crawl()


def main():

    def get_session_type():
        """
        Ask the user what type of scraping session they would like to initiate.
        :return: The appropriate class to be used.
        """
        sesh_types = ['Scrape - Get Info <i>', 'Scrape - Get Links <l>', 'Download File - Get Files <d>']
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
            elif 'd' in type_resp:
                return LinkFileType
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
            Convert the input into a list. If the input has commas, separate entries from the commas
            convert it to a list.
            :param links: inputted url(s).
            :return: a list of urls or a list with one url
            """
            if ',' in links:
                links = links.split(',')
                links = [i.strip() for i in links]
                return set(links)
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
            else:
                return multiprocess(initiate_scrape_reg, url_regex_tup)

        def create_link_key():
            """
            Initiate link_key
            :return: Output of link_key.crawl()
            """
            url = input('Enter URL or a list of urls separated by a comma\n: ').lower()
            url_list = list_or_string(url)
            # todo: TEST THIS: turn url_list into a set list, just in case the same url is added into the input list twice
            regex = input('Enter the Regular Expression of the info you would like to extract\n: ').lower()
            url_regex_tup = [(url, regex) for url in url_list]

            if len(url_list) == 1:
                return LinkKey(url.rstrip(), regex).crawl()
            else:
                return multiprocess(initiate_link_key, url_regex_tup)

        def create_link_file_type():
            """
            Initiate link_file_type
            :return: Output of link_file_type.crawl()
            """

            def create_file_dict():
                """
                Create a dictionary of the file types to search for using user input.
                :return: dict(file_extension: mimetype)
                """

                def get_extensions():
                    """
                    User inputs extensions they would like to download.
                    :return: dict(file_extension: mimetype)
                    """
                    file_dict = {}
                    while True:
                        # print the file_dict
                        if file_dict:
                            print('File to scrape:')
                            for file in file_dict.keys():
                                print(f'\t--> {file}')
                        get_file_type = input('Enter a file type? Enter <s> to start crawl\n: ').lower()

                        if get_file_type:
                            # exit chain
                            if get_file_type == 's':
                                if not file_dict:
                                    print("You didn't enter any valid file types. Exiting.")
                                    return
                                break
                            elif get_file_type == 'h':
                                for key in mimetypes.types_map.keys():
                                    print(key)

                            # confirm the extension is a mimetype
                            for extension, mtype in mimetypes.types_map.items():

                                # add a leading dot if there isn't one
                                if not get_file_type.startswith('.'):
                                    get_file_type = '.' + get_file_type

                                # check if there's a match, add to dict if is
                                if get_file_type in extension:
                                    file_dict[get_file_type] = mtype
                                    break
                        else:
                            print('File type is invalid. Enter <h> for valid file types.', file=sys.stderr)
                    return file_dict

                def confirm_extensions(file_dict):
                    """
                    Confirm the file dictionary is correct with the user. Delete entry's the user would like to remove
                    :param file_dict: dict(file_extension: mimetype)
                    :return: dict(file_extension: mimetype)
                    """

                    # confirm list
                    while True:
                        print('Final File List:')
                        for file in file_dict.keys():
                            print(f'\t--> {file}')

                        # confirm list
                        ans = input('Press <ENTER> to begin crawl. Enter <D> to delete a file.').lower()
                        if not ans:
                            break

                        if 'd' in ans:
                            while True:
                                print('Enter the file extension (accurately) to be deleted. Enter <q> to exit.')
                                for file in file_dict.keys():
                                    print(f'--> {file}')

                                # get index number, and delete the entry
                                res = input(': ').lower()

                                # exit chain
                                if 'q' in res:
                                    break

                                # delete chain
                                try:
                                    del file_dict[res]
                                    print(f'Removed {res}', file=sys.stderr)
                                    break
                                except KeyError:
                                    print('Make sure your entry is accurate!')
                    print('File list: CONFIRMED!')
                    return file_dict

                extension_dict = get_extensions()
                confirm_extension = confirm_extensions(extension_dict)
                return confirm_extension
            # TODO: create a function that creates a user list. this function can be used at the top of
            #   create_scrape_reg, create_link_key and create_link_file_type
            url = input('Enter URL or a list of urls separated by a comma\n: ').lower()
            url_list = list_or_string(url)
            # build a file list
            file_dict = create_file_dict()

            # remove this list when LinkFileType has been refactored
            extension_list = [i for i in file_dict.keys()]

            # begin crawl
            if len(url_list) == 1:
                return LinkFileType(url.rstrip(), extension_list).crawl()

                # use the line below when LinkFileType has been refactored to handle a dictionary
                # return LinkFileType(url.rstrip(), file_dict)
            else:
                url_extension_list_tup = [(url, extension_list) for url in url_list]
                return multiprocess(initiate_link_file_type, url_extension_list_tup)

                # use the lines below when LinkFileType has been refactored to handle a dictionary
                # url_file_dict_tup = [(url, file_dict) for url in url_list]
                # return multiprocess(initiate_link_file_type, url_file_dict_tup)

        sesh_type = get_session_type()

        if sesh_type == ScrapeReg:
            create_scrape_reg()
        elif sesh_type == LinkKey:
            create_link_key()
        elif sesh_type == LinkFileType:
            create_link_file_type()

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

        def get_saved_sessions(sesh_type):
            """
            Get a list of the saved .db files in the ./save directory
            :return: A list of the name of the saved .db files
            """
            # use the appropriate path
            if sesh_type == Crawl:
                path = './save/crawl'
            elif sesh_type == LinkKey:
                path = './save/link_key'
            elif sesh_type == LinkFileType:
                path = './save/link_filetype'
            elif sesh_type == ScrapeReg:
                path = './save/scrape_reg'
            else:
                print('Impossible!')
                print(sesh_type)
                return

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

        def create_crawl_objects(sesh_type, sesh_list):
            """
            Create crawl objects for each file_name in session list.
            :param sesh_type: the class being used to crawl
            :param sesh_list: list of sessions to create crawl objects
            :return: A list of crawl objects
            """
            return [sesh_type.from_save(session) for session in sesh_list]

        def get_session_list(sesh_type):
            """
            Get a list of sessions that the user wishes to resume.
            :param sesh_type: class being used
            :return: A list of session names
            """
            session_list = []
            printed_files_list = get_saved_sessions(sesh_type)
            while True:
                if not printed_files_list:
                    # if the user enters in all of the saved sessions
                    print('You have added all of the session saves to your resume list, press [ENTER] to initiate crawls')
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
        session_list = get_session_list(sesh_type)

        # if the user didn't add any session names to the Resume Session List
        if not session_list:
            return print('Sessions not added to Resume Session List')

        # create a list of crawl objects
        session_objects = create_crawl_objects(sesh_type, session_list)

        # if the user wishes to resume crawl of one list, don't use multiprocessing
        if len(session_list) == 1:
            crawl_object = session_objects[0]
            outputs = resume_crawl(crawl_object)
            return print(outputs)

        multiprocess(resume_crawl, session_objects)

    def setup_folders():
        """
        Build out the directory.
        :return: None
        """

        # create downloads
        if not os.path.exists('downloads'):
            os.mkdir('downloads')

        # create save and its sub-directories
        if not os.path.exists('save'):
            os.mkdir('save')

            # create sub-directories
            os.mkdir('./save/crawl')
            os.mkdir('./save/link_filetype')
            os.mkdir('./save/link_key')
            os.mkdir('./save/scrape_reg')

    print('Welcome to Scraper!')

    # setup folders
    setup_folders()

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
            print('Invalid entry')
    except KeyboardInterrupt:
        print('quitting...')


if __name__ == '__main__':
    main()
