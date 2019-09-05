import os
import multiprocessing
from crawl import Crawl


def initiate_crawl(url):
    """Crawl a given url with multiprocessing"""
    Crawl(url).crawl()


def resume_crawl(crawl_object):
    """
    Resume a crawl.
    :param crawl_object: The Crawl object
    :return: None
    """
    crawl_object.crawl()

def main():
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

        # initiate multithreading if the user submits a list of urls
        list_count = len(url_list)
        thread_count = multiprocessing.cpu_count() * 2

        # create a pool size the size of the list, if the list is larger than the machines thread count, use max threads
        if list_count > thread_count:
            pool_size = thread_count
        else:
            pool_size = list_count
        pool = multiprocessing.Pool(
            processes=pool_size
        )
        pool_outputs = pool.map(initiate_crawl, url_list)  # todo: create a return statement for .crawl: TEST ME!
        pool.close()
        pool.join()
        print(pool_outputs)

    def resume_sesh():
        """
        List saved crawl sessions, and then resume crawl session.
        :return: None
        """

        def print_sesh_list(sesh_lis):
            """
            Print the current session list.
            :param sesh_lis: The current session list
            :return:
            """
            if not sesh_lis:
                print('Resume Session List:\n\tCurrently Empty :(')
            else:
                print('Resume Session list:')
                for session in session_list:
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

                if filename not in printed_files_list:
                    printed_files_list.append(filename)
            return printed_files_list

        def create_crawl_objects(session_list):
            """
            Create crawl objects for each file_name in session list.
            :param session_list: list of sessions to create crawl objects
            :return: A list of crawl objects
            """
            return [Crawl.from_save(session) for session in session_list]

        print('|Enter the sessions you wish to resume|Enter [Q] to initiate crawl sessions')

        # todo: create a code block that asks the user which sessions they would like to resume and
        #  resume the sessions using multiprocessing
        session_list = []
        printed_files_list = get_saved_sessions()
        while True:
            if not printed_files_list:
                print('You have added all of the session saves to your resume list, press [ENTER] to initiate crawls.')
                input(': ')
                break
            print_saved_sessions(printed_files_list)
            print_sesh_list(session_list)
            session_name = input(': ')
            if session_name in printed_files_list:
                session_list.append(session_name)
                # print(f'{session_name} added to resume session list')
                printed_files_list.remove(session_name)
            elif session_name in session_list:
                print(f'{session_name} already in resume session list')
            elif session_name == 'q':
                break
            else:
                print(f'Session not found: {session_name}')
        if not session_list:
            return print('Session names were not added to the Resume Session List')

        # create a list of crawl objects
        crawl_objects = create_crawl_objects(session_list)

        # if the user wishes to resume crawl of one list, don't use multiprocessing
        if len(session_list) < 2:
            crawl_object = crawl_objects[0]
            outputs = crawl_object.crawl()
            return print(outputs)

        # multiprocess crawl threads
        list_count = len(crawl_objects)
        thread_count = multiprocessing.cpu_count() * 2
        # create a pool size the size of the list, if the list is larger than the machines thread count, use max threads
        if list_count > thread_count:
            pool_size = thread_count
        else:
            pool_size = list_count

        print(pool_size)
        print(session_list)
        # initiate multiprocessing pool
        pool = multiprocessing.Pool(
            processes=pool_size
        )
        pool_outputs = pool.map(resume_crawl, crawl_objects)  # todo: create a function with the parameters of initial function and the iterable of args
        pool.close()
        pool.join()
        print(pool_outputs)

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

