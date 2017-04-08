# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import logging
from django.conf import settings

DEFAULT_APP_NAME = 'django_cbrf'
CBRF_APP_NAME = getattr(settings, 'CBRF_APP_NAME', DEFAULT_APP_NAME)
DAYS_FOR_POPULATE = getattr(settings, 'CBRF_DAYS_FOR_POPULATE', 60)

DEBUG = getattr(settings, 'DEBUG', True)

if DEBUG:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')