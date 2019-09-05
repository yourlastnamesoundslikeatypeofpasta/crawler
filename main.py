import os
import multiprocessing
from crawl import Crawl


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


def main():

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

        pool_size = create_pool_size(iterable)
        pool = multiprocessing.Pool(
            processes=pool_size
        )
        pool_outputs = pool.map(func, iterable)
        pool.close()
        pool.join()

        return print(pool_outputs)

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
                return [links]

        # ask the user if they're submitting one new_urls or a list of urls
        url = input('Enter URL or a list of urls separated by a comma\n: ').lower()
        url_list = list_or_string(url)

        # if the user wishes to scrape one url, don't use multiprocessing
        if len(url_list) == 1:
            url = url_list[0]
            output = initiate_crawl(url)
            return output

        # initiate multiprocessing
        multiprocess(initiate_crawl, url_list)

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
    try:
        while True:
            print('[NEW SESSION] or [RESUME SESSION] or [QUIT] [N/R/Q]')
            sesh_response = input(': ').lower()  # todo: introduce session types
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

