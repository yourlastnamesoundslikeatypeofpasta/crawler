import re


def get_email_from_unicode(string):
    """
    Decodes emails encoded in ASCII
    :param string: Encoded email string ex. https://pastebin.com/me4cN38Y
    :return: A decoded string containing the email.
    """
    unicode_email_lst = list(string)
    avoid_char_list = ['&', '#', '>']
    num_list = [str(i) for i in range(10)]
    possible_email_list = []

    # unicode char are represented by values that are either 2-3 in length. ex. 23, 110, 64
    unicode_char = ''

    # Decode email
    for char in unicode_email_lst:
        # Avoid these seemingly random characters
        if char in avoid_char_list:
            continue
        elif char in num_list:
            # Create unicode_char
            unicode_char = unicode_char + char
            continue
        elif char == ';':
            # Each unicode character is seperated by a ';'
            possible_email_list.append(chr(int(unicode_char)))
            unicode_char = ''
            continue
        else:
            # Append characters that aren't encoded
            possible_email_list.append(char)

    # Extract email using some regex magic
    email_string = ''.join(possible_email_list)
    email = list(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", email_string, re.I))[0]
    return email

# TODO: REMINDER: ENCODED EMAIL REGEX <a href="([&#]+\d+;)+"
