import datetime
from dateutil import parser

from infrastructure.switchlang import switch
import program_hosts as hosts
import services.data_service as svc
from program_hosts import success_msg, error_msg
import infrastructure.state as state


def run():
    print(' ****************** Welcome guest **************** ')
    print()

    show_commands()

    while True:
        action = hosts.get_action()

        with switch(action) as s:
            s.case('c', hosts.create_account)
            s.case('l', hosts.log_into_account)

            s.case('a', add_a_item)
            s.case('y', view_your_items)
            s.case('b', book_a_locker)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')

            s.case('?', show_commands)
            s.case('', lambda: None)
            s.case(['x', 'bye', 'exit', 'exit()'], hosts.exit_app)

            s.default(hosts.unknown_command)

        state.reload_account()

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[B]ook a locker')
    print('[A]dd a item')
    print('View [y]our items')
    print('[V]iew your bookings')
    print('[M]ain menu')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def add_a_item():
    print(' ****************** Add a item **************** ')
    if not state.active_account:
        error_msg("You must log in first to add a item")
        return

    name = input("What is your item? ")
    if not name:
        error_msg('cancelled')
        return

    sizing = float(input('How big is your item (in meters)? '))

    item = svc.add_item(state.active_account, name, sizing)
    state.reload_account()
    success_msg('Created {} with id {}'.format(item.name, item.id))


def view_your_items():
    print(' ****************** Your items **************** ')
    if not state.active_account:
        error_msg("You must log in first to view your items")
        return

    items = svc.get_items_for_user(state.active_account.id)
    print("You have {} items.".format(len(items)))
    for s in items:
        print(" * {} is {}m big.".format(
            s.name,
            s.sizing,
        ))


def book_a_locker():
    print(' ****************** Book a locker **************** ')
    if not state.active_account:
        error_msg("You must log in first to book a locker")
        return

    items = svc.get_items_for_user(state.active_account.id)
    if not items:
        error_msg('You must first [a]dd a item before you can book a locker.')
        return

    print("Let's start by finding available lockers.")
    start_text = input("Check-in date [yyyy-mm-dd]: ")
    if not start_text:
        error_msg('cancelled')
        return

    checkin = parser.parse(
        start_text
    )
    checkout = parser.parse(
        input("Check-out date [yyyy-mm-dd]: ")
    )
    if checkin >= checkout:
        error_msg('Check in must be before check out')
        return

    print()
    for idx, s in enumerate(items):
        print('{}. {} (sizing: {})'.format(
            idx + 1,
            s.name,
            s.sizing,
        ))

    item = items[int(input('Which item do you want to book (number)')) - 1]

    lockers = svc.get_available_lockers(checkin, checkout, item)

    print("There are {} lockers available in that time.".format(len(lockers)))
    for idx, c in enumerate(lockers):
        print(" {}. {} with {}m.".format(
            idx + 1,
            c.name,
            c.square_meters))

    if not cages:
        error_msg("Sorry, no lockers are available for that date.")
        return

    locker = lockers[int(input('Which locker do you want to book (number)')) - 1]
    svc.book_locker(state.active_account, item, locker, checkin, checkout)

    success_msg('Successfully booked {} for {} at ${}/night.'.format(locker.name, item.name, locker.price))


def view_bookings():
    print(' ****************** Your bookings **************** ')
    if not state.active_account:
        error_msg("You must log in first to register a locker")
        return

    items = {s.id: s for s in svc.get_items_for_user(state.active_account.id)}
    bookings = svc.get_bookings_for_user(state.active_account.email)

    print("You have {} bookings.".format(len(bookings)))
    for b in bookings:
        # noinspection PyUnresolvedReferences
        print(' * Item: {} is booked at {} from {} for {} days.'.format(
            items.get(b.guest_item_id).name,
            b.cage.name,
            datetime.date(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day),
            (b.check_out_date - b.check_in_date).days
        ))
