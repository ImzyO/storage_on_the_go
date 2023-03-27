#!/usr/bin/env python3
"""owners module"""

import datetime
import mongoengine


class Owner(mongoengine.Document):
    """class owners with attribute name and email,
    and day owner registered"""
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    name = mongoengine.StringField(required=True)
    email = mongoengine.StringField(required=True)

    item_ids = mongoengine.ListField()
    locker_ids = mongoengine.ListField()

    meta = {
        'db_alias': 'core',
        'collection': 'owners'
    }
