#!/usr/bin/env python3
"""mongo steup module"""

import mongoengine


def global_init():
    """function allows for calling from multiple
    databases, the core is the alias,
    name of database is Rescue_heroes"""
    mongoengine.register_connection(alias='core', name='Rescue_Heroes')
