#!/usr/bin/env python3
"""items module"""

import datetime
import mongoengine


class Item(mongoengine.Document):
    """function item with attributes, sizing of the item,
    name of the items to be stored"""
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    sizing = mongoengine.FloatField(required=True)
    name = mongoengine.StringField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'items'
    }
