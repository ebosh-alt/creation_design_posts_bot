import random
import string
from bot.config import link_bot


def add_link(link):
    with open("../db/invoice_link.txt", "a") as f:
        f.write(link + "\n")


def get_links():
    data = []
    with open("../db/invoice_link.txt", "r") as f:
        data = f.read()
    return data.split("\n")


def get_invoice_link(length):
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for i in range(length))
    link = f"{link_bot}?start=inv_{rand_string}"
    add_link(link)
    return link


if __name__ == '__main__':
    print(get_invoice_link(25))
