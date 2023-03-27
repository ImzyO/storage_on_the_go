#!/usr/bin/env python3
"""program main, where prgram runs module"""

from colorama import Fore
import program_guests
import program_hosts
import models.mongo_setup as mongo_setup


def main():
    mongo_setup.global_init()

    print_header()

    try:
        while True:
            if find_user_intent() == 'book':
                program_guests.run()
            else:
                program_hosts.run()
    except KeyboardInterrupt:
        return


def print_header():
    smiley = \
        """
                                   ..........
                                   ..&@...@,...
                                  ....%...@....
                                  ../.......@.(
                                    (.......(  """


    print(Fore.WHITE + '****************  storage on the go  ****************')
    print(Fore.YELLOW + smiley)
    print(Fore.WHITE + '*********************************************')
    print()
    print("Welcome to storage on the go!")
    print("Why are you here?")
    print()


def find_user_intent():
    print("[g] Book a locker for your items")
    print("[h] Offer extra locker space")
    print()
    choice = input("Are you a [g]uest or [h]ost? ")
    if choice == 'h':
        return 'offer'

    return 'book'


if __name__ == '__main__':
    main()
