import os
import multiprocessing
from crawl import Crawl


def initiate_crawl(url):
    """Crawl a given url with multiprocessing"""
    Crawl(url).crawl()


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
                print('Session list:\n\tCurrently Empty :(')
            else:
                for session in session_list:
                    print(f'\t{session}')
        print('|Enter the sessions you wish to resume|Enter [Q] to initiate crawl sessions')

        # print out saved .db files
        path = './save'
        dirs = os.listdir(path)
        printed_files_list = []
        for file in dirs:
            filename, file_extension = os.path.splitext(file)

            # the shelve module occasionally creates other files along with the .db
            if file_extension != '.db':
                filename, file_extension = os.path.splitext(filename)

            if filename not in printed_files_list:
                print(filename)
                printed_files_list.append(filename)


        # todo: create a code block that asks the user which sessions they would like to resume and
        #  resume the sessions using multiprocessing
        session_list = []
        while True:
            print_sesh_list(session_list)
            session_name = input(': ').lower()
            if session_name in printed_files_list:
                session_list.append(session_name)
                print(f'{session_name} added to resume session list')
                print('Session list:')
                for session in session_list:
                    print(f'\t{session}')
            elif session_name == 'q':
                break
            else:
                print(f'Session not found: {session_name}')




        url = Crawl.from_save(save_file)
        url.crawl()

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

