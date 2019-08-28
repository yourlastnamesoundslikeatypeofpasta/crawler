from scraper_class import Scraper
import os


def main():
    def new_sesh():
        """
        Create a new crawl session, and then crawl.
        :return: None
        """
        # ask the user if they're submitting one url or a list of urls
        # todo: check if the inputted string has commas and convert to list if it,
        #  instead of asking the user if they're entering a string or a list.
        from_string_or_list = input('Would you like to scrape a list of urls or one url? [L/S]\n: ').lower()
        if from_string_or_list == 'l':
            url_list = input('Enter your urls separated with a comma\n: ')
            input_url = url_list.split(',')
            input_url = [i.strip() for i in input_url]
        else:
            input_url = input('Enter your url\n: ')
        url = Scraper(input_url)
        url.sleep_time = 2
        url.scrape()

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
        url = Scraper.from_save(save_file)
        url.scrape()

    print('Welcome to Scraper!')
    try:
        while True:
            print('[NEW SESSION] or [RESUME SESSION] or [QUIT] [N/R/Q]')
            sesh_response = input(': ').lower()
            if sesh_response == 'n':
                new_sesh()
            elif sesh_response == 'r':
                resume_sesh()
            elif sesh_response == 'q':
                print('quitting')
                break
            else:
                print('Invalid entry')
    except KeyboardInterrupt:
        print('quitting')


if __name__ == '__main__':
    main()

