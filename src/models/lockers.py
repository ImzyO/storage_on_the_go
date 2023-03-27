#!/usr/bin/env python3
"""lockers module"""

import datetime
import mongoengine

from models.bookings import Booking


class Locker(mongoengine.Document):
    """class locker with attributes name of locker,
    price of locker, locker squaremetres,
    locker registration date"""
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    name = mongoengine.StringField(required=True)
    price = mongoengine.FloatField(required=True)
    square_meters = mongoengine.FloatField(required=True)

    bookings = mongoengine.EmbeddedDocumentListField(Booking)

    meta = {
        'db_alias': 'core',
        'collection': 'lockers'
    }
