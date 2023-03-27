#!/usr/bin/env python3
"""bookings module"""

import mongoengine


class Booking(mongoengine.EmbeddedDocument):
    """class booking with attributes date,
    time, review, rating"""
    guest_owner_id = mongoengine.ObjectIdField()
    guest_item_id = mongoengine.ObjectIdField()

    booked_date = mongoengine.DateTimeField()
    item_in_date = mongoengine.DateTimeField(required=True)
    item_out_date = mongoengine.DateTimeField(required=True)

    review = mongoengine.StringField()
    rating = mongoengine.IntField(default=0)

    @property
    def duration_in_days(self):
        """function duration counting number of days
        item is booked for in storage locker"""
        duration = self.item_out_date - self.item_in_date
        return duration.days
