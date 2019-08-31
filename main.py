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

        # ask the user if they're submitting one new_urls or a list of urls
        # todo: check if the inputted string has commas and convert to list if it,
        #  instead of asking the user if they're entering a string or a list.
        from_string_or_list = input('Would you like to crawl a list of urls or one new_urls? [L/S]\n: ').lower()
        if from_string_or_list == 'l':
            url_list = input('Enter your urls separated with a comma\n: ')
            input_url = url_list.split(',')
            input_url = [i.strip().lower() for i in input_url]
        else:
            input_url = input('Enter your new_urls\n: ')
        session_name = get_name_session()
        url = Crawl(session_name, input_url)
        url.sleep_time = 2
        url.crawl()

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

