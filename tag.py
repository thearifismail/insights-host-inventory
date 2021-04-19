import random
import string

tag = "".join(random.choices(string.ascii_letters + string.digits, k=7))
print(tag)
