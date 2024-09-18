import string
import random

def random_passwd():
    len = 10
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(len))