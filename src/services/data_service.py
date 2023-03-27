#!/usr/bin/env python3
"""data access code module"""

from typing import List, Optional

import datetime

import bson

from models.bookings import Booking
from models.lockers import Locker
from models.owners import Owner
from models.items import Item


def create_account(name: str, email: str) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email

    owner.save()

    return owner


def find_account_by_email(email: str) -> Owner:
    owner = Owner.objects(email=email).first()
    return owner


def register_locker(active_account: Owner,
                  name, price, metres) -> Locker:
    locker = Locker()

    locker.name = name
    locker.square_meters = meters
    locker.price = price

    locker.save()

    account = find_account_by_email(active_account.email)
    account.locker_ids.append(locker.id)
    account.save()

    return locker


def find_lockers_for_user(account: Owner) -> List[Locker]:
    query = Locker.objects(id__in=account.locker_ids)
    lockers = list(query)

    return lockers


def add_available_date(locker: Locker,
                       start_date: datetime.datetime, days: int) -> Locker:
    booking = Booking()
    booking.check_in_date = start_date
    booking.check_out_date = start_date + datetime.timedelta(days=days)

    locker = Locker.objects(id=locker.id).first()
    locker.bookings.append(booking)
    locker.save()

    return locker


def add_item(account, name, sizing) -> Item:
    item = Item()
    item.name = name
    item.sizing = sizing
    
    item.save()

    owner = find_account_by_email(account.email)
    owner.item_ids.append(item.id)
    owner.save()

    return item


def get_items_for_user(user_id: bson.ObjectId) -> List[Item]:
    owner = Owner.objects(id=user_id).first()
    items = Item.objects(id__in=owner.item_ids).all()

    return list(items)


def get_available_lockers(checkin: datetime.datetime,
                        checkout: datetime.datetime, item: Item) -> List[Locker]:
    min_size = item.sizing / 4

    query = Locker.objects() \
        .filter(square_meters__gte=min_size) \
        .filter(bookings__check_in_date__lte=checkin) \
        .filter(bookings__check_out_date__gte=checkout)

    lockers = query.order_by('price', '-square_meters')

    final_lockers = []
    for c in lockers:
        for b in c.bookings:
            if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_item_id is None:
                final_lockers.append(c)

    return final_lockers


def book_locker(account, item, locker, checkin, checkout):
    booking: Optional[Booking] = None

    for b in locker.bookings:
        if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_item_id is None:
            booking = b
            break

    booking.guest_owner_id = account.id
    booking.guest_item_id = item.id
    booking.check_in_date = checkin
    booking.check_out_date = checkout
    booking.booked_date = datetime.datetime.now()

    locker.save()


def get_bookings_for_user(email: str) -> List[Booking]:
    account = find_account_by_email(email)

    booked_cages = Cage.objects() \
        .filter(bookings__guest_owner_id=account.id) \
        .only('bookings', 'name')

    def map_cage_to_booking(cage, booking):
        booking.cage = cage
        return booking

    bookings = [
        map_cage_to_booking(cage, booking)
        for cage in booked_cages
        for booking in cage.bookings
        if booking.guest_owner_id == account.id
    ]

    return bookings
