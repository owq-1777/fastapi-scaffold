import string
import random


def random_str(length=16):
    """ Generates a random string of a specified length """

    letters = string.ascii_lowercase + string.digits
    result_str = ''.join(random.choice(letters) for _ in range(length))
    return result_str