# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

"""
    Settings for project with default volumes.
"""

from django.conf import settings

__all__ = ['CURRENCIES', 'INIT_RATES_DAYS']

CURRENCIES = getattr(settings, 'CBRF_CURRENCIES', [])
INIT_RATES_DAYS = getattr(settings, 'CBRF_INIT_RATES_DAYS', 30)
