#!/usr/bin/env python3
"""module with program host code prompt"""

import datetime
from colorama import Fore
from dateutil import parser

from infrastructure.switchlang import switch
import infrastructure.state as state
import services.data_service as svc


def run():
    print(' ****************** Welcome host **************** ')
    print()

    show_commands()

    while True:
        action = get_action()

        with switch(action) as s:
            s.case('c', create_account)
            s.case('a', create_account)
            s.case('l', log_into_account)
            s.case('y', list_lockers)
            s.case('r', register_locker)
            s.case('u', update_availability)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')
            s.case(['x', 'bye', 'exit', 'exit()'], exit_app)
            s.case('?', show_commands)
            s.case('', lambda: None)
            s.default(unknown_command)

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an [a]ccount')
    print('[L]ogin to your account')
    print('List [y]our lockers')
    print('[R]egister a locker')
    print('[U]pdate locker availability')
    print('[V]iew your bookings')
    print('Change [M]ode (guest or host)')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def create_account():
    print(' ****************** REGISTER **************** ')

    name = input('What is your name? ')
    email = input('What is your email? ').strip().lower()

    old_account = svc.find_account_by_email(email)
    if old_account:
        error_msg(f"ERROR: Account with email {email} already exists.")
        return

    state.active_account = svc.create_account(name, email)
    success_msg(f"Created new account with id {state.active_account.id}.")


def log_into_account():
    print(' ****************** LOGIN **************** ')

    email = input('What is your email? ').strip().lower()
    account = svc.find_account_by_email(email)

    if not account:
        error_msg(f'Could not find account with email {email}.')
        return

    state.active_account = account
    success_msg('Logged in successfully.')


def register_locker():
    print(' ****************** REGISTER LOCKER **************** ')

    if not state.active_account:
        error_msg('You must login first to register a locker.')
        return

    meters = input('How many square meters is the locker? ')
    if not meters:
        error_msg('Cancelled')
        return

    meters = float(meters)
    name = input("Give your locker a name: ")
    price = float(input("How much are you charging?  "))

    locker = svc.register_locker(
        state.active_account, name,
        meters, price
    )

    state.reload_account()
    success_msg(f'Register new locker with id {locker.id}.')


def list_lockers(suppress_header=False):
    if not suppress_header:
        print(' ******************     Your lockers     **************** ')

    if not state.active_account:
        error_msg('You must login first to register a locker.')
        return

    lockers = svc.find_lockers_for_user(state.active_account)
    print(f"You have {len(lockers)} lockers.")
    for idx, c in enumerate(lockers):
        print(f' {idx + 1}. {c.name} is {c.square_meters} meters.')
        for b in c.bookings:
            print('      * Booking: {}, {} days, booked? {}'.format(
                b.check_in_date,
                (b.check_out_date - b.check_in_date).days,
                'YES' if b.booked_date is not None else 'no'
            ))


def update_availability():
    print(' ****************** Add available date **************** ')

    if not state.active_account:
        error_msg("You must log in first to register a locker")
        return

    list_lockers(suppress_header=True)

    locker_number = input("Enter locker number: ")
    if not locker_number.strip():
        error_msg('Cancelled')
        print()
        return

    locker_number = int(locker_number)

    lockers = svc.find_lockers_for_user(state.active_account)
    selected_locker = lockers[locker_number - 1]

    success_msg("Selected locker {}".format(selected_locker.name))

    start_date = parser.parse(
        input("Enter available date [yyyy-mm-dd]: ")
    )
    days = int(input("How many days is this block of time? "))

    svc.add_available_date(
        selected_locker,
        start_date,
        days
    )

    success_msg(f'Date added to locker {selected_locker.name}.')


def view_bookings():
    print(' ****************** Your bookings **************** ')

    if not state.active_account:
        error_msg("You must log in first to register a locker")
        return

    lockers = svc.find_lockers_for_user(state.active_account)

    bookings = [
        (c, b)
        for c in lockers
        for b in c.bookings
        if b.booked_date is not None
    ]

    print("You have {} bookings.".format(len(bookings)))
    for c, b in bookings:
        print(' * Locker: {}, booked date: {}, from {} for {} days.'.format(
            c.name,
            datetime.date(b.booked_date.year, b.booked_date.month, b.booked_date.day),
            datetime.date(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day),
            b.duration_in_days
        ))


def exit_app():
    print()
    print('bye')
    raise KeyboardInterrupt()


def get_action():
    text = '> '
    if state.active_account:
        text = f'{state.active_account.name}> '

    action = input(Fore.YELLOW + text + Fore.WHITE)
    return action.strip().lower()


def unknown_command():
    print("Sorry we didn't understand that command.")


def success_msg(text):
    print(Fore.LIGHTGREEN_EX + text + Fore.WHITE)


def error_msg(text):
    print(Fore.LIGHTRED_EX + text + Fore.WHITE)
