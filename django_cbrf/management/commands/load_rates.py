# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import datetime
import logging

from django.core.management import BaseCommand
from django.utils.timezone import now

from django_cbrf.utils import get_cbrf_model
from ...settings import DAYS_FOR_POPULATE

logger = logging.getLogger(__name__)

Currency = get_cbrf_model('Currency')
Record = get_cbrf_model('Record')


class Command(BaseCommand):
    """ Load currency rate records frim cbr.ru """

    help = """ 
Download rates for selected currencies from today back to today minus '--days' argument value.

For example, command like:

    `manage.py load_rates USD RUB --days 90`
    
will populate rates for $ and ₽ for last 90 days.
    """

    def add_arguments(self, parser):
        parser.add_argument('iso_codes', nargs='+', type=str)
        parser.add_argument('--days', type=int, default=DAYS_FOR_POPULATE)

    def handle(self, *args, **options):
        days = options['days']
        currencies = options['iso_codes']

        if not Currency.objects.all():
            logger.info("No one Currency in DB. Populating...")
            Currency.populate()

        date_1 = now().date() - datetime.timedelta(days=days)
        date_2 = now().date()

        for currency_iso in currencies:
            currency = Currency.get_by_iso_char_code(currency_iso.upper())
            if currency:
                logger.info("Get rates for '{}'".format(currency.eng_name))
                Record.populate_for_dates(date_1, date_2, currency)
            else:
                logger.error("Currency with '{}' ISO code is not exist. Skipped.".format(currency_iso))
