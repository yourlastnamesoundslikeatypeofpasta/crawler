import os

from crawl import Crawl


def main():
    def new_sesh():
        """
        Create a new crawl session, and then crawl.
        :return: None
        """

        def get_name_session():
            """
            Get the name of this crawl session from the user.
            :return: a string of the name of the session
            """
            # chars not allowed
            illegal_char_list = ['\\', '/', ':', 'NUL', ':', '*', '"', '<', '>', '|']
            while True:
                ns = input('What would you like to name this crawl session?\n:').lower().strip()

                # check if the name session has any illegal character
                illegal_char = False
                for char in ns:
                    if char in illegal_char_list:
                        print(f'IllegalCharacter: {char}. Your session name cannot have the following characters:')
                        print(','.join(illegal_char_list))
                        illegal_char = True
                        break
                if illegal_char:
                    continue
                else:
                    return ns

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

        session_name = get_name_session()

        # ask the user if they're submitting one new_urls or a list of urls
        url = input('Enter URL or a list of urls separated by a comma\n: ').lower()
        url_list = list_or_string(url)
        Crawl(session_name, url_list).crawl()

    def resume_sesh():
        """
        List saved crawl sessions, and then resume crawl session.
        :return: None
        """
        print('Please select a save file:')

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
        save_file = input(': ')
        url = Crawl.from_save(save_file)
        url.crawl()

    print('Welcome to Scraper!')
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

