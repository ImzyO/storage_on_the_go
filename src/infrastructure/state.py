#!/usr/bin/env python3
"""accounts module"""

from typing import Optional

from models.owners import Owner
import services.data_service as svc

active_account: Optional[Owner] = None


def reload_account():
    global active_account
    if not active_account:
        return

    active_account = svc.find_account_by_email(active_account.email)
