import random
import string
def generate_random_seed():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))