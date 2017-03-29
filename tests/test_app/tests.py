import logging
from datetime import datetime
from decimal import Decimal

from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase

from django_cbrf import settings
from django_cbrf.utils import get_cbrf_model

Currency = get_cbrf_model('Currency')
Record = get_cbrf_model('Record')


class CBRFManagementCommandsTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def test_load_currencies(self):
        """ Try to populate Currencies """

        self.assertEqual(len(Currency.objects.all()), 0)
        call_command('load_currencies')
        self.assertEqual(len(Currency.objects.all()), 60)

        with self.assertRaisesMessage(IntegrityError,
                                      'Currencies already populated. '
                                      'To force populate use "python manage.py '
                                      'load_currencies --force"'):
            call_command('load_currencies')

        Currency.objects.first().delete()
        self.assertEqual(len(Currency.objects.all()), 59)

        call_command('load_currencies', '--force')
        self.assertEqual(len(Currency.objects.all()), 60)

    def test_load_rates(self):
        """ Try to populate some rates records """
        self.assertEqual(len(Record.objects.all()), 0)

        call_command('load_rates', 'usd')
        self.assertNotEqual(len(Record.objects.all()), 0)

        Record.objects.all().delete()
        call_command('load_rates', 'usd', '--days', '16')
        self.assertNotEqual(len(Record.objects.all()), 0)

        # few currencies
        Record.objects.all().delete()
        call_command('load_rates', 'usd', 'eur')
        self.assertNotEqual(len(Record.objects.all()), 0)


class CurrencyTestCase(TestCase):
    def setUp(self):
        Currency.populate()
        logging.disable(logging.CRITICAL)

    def test_get_by_cbrf_id(self):
        cbrf_id = 'R01500'
        bad_cbrf_id = 'meh'

        self.assertEqual(Currency.get_by_cbrf_id(cbrf_id).eng_name, 'Moldova Lei')
        self.assertIsNone(Currency.get_by_cbrf_id(bad_cbrf_id))

    def test_get_by_iso_num(self):
        iso_int = 840
        iso_str = '840'

        self.assertEqual(Currency.get_by_iso_num_code(iso_int).cbrf_id, 'R01235')
        self.assertEqual(Currency.get_by_iso_num_code(iso_str).cbrf_id, 'R01235')

        bad_iso = 999

        self.assertIsNone(Currency.get_by_iso_num_code(bad_iso))

    def test_get_by_iso_char(self):
        iso = 'USD'

        self.assertEqual(Currency.get_by_iso_char_code(iso).cbrf_id, 'R01235')

        bad_iso = 'LOL'

        self.assertIsNone(Currency.get_by_iso_char_code(bad_iso))


class RecordsTestCase(TestCase):
    def setUp(self):
        Currency.populate()

    def test_populate_for_dates(self):
        date_1 = datetime(2001, 3, 2)
        date_2 = datetime(2001, 3, 14)

        usd = Currency.objects.get(cbrf_id='R01235')

        rates = Record._populate_for_dates(date_1, date_2, usd)
        self.assertEqual(len(rates), 8)
        self.assertEqual(rates.filter(date__year=2001, date__month=3, date__day=2).first().value, Decimal('28.6200'))
        self.assertEqual(rates.filter(date__year=2001, date__month=3, date__day=3).first().value, Decimal('28.6500'))
        self.assertEqual(rates.filter(date__year=2001, date__month=3, date__day=6).first().value, Decimal('28.6600'))
        self.assertEqual(rates.filter(date__year=2001, date__month=3, date__day=7).first().value, Decimal('28.6300'))

    def test_get_for_dates(self):
        self.assertEqual(len(Record.objects.all()), 0)

        usd = Currency.objects.get(cbrf_id='R01235')

        date_1 = datetime(2001, 3, 2)
        date_2 = datetime(2001, 3, 14)

        Record.get_for_dates(date_1, date_2, usd)

        self.assertEqual(len(Record.objects.all()), 8)


class CustomSettingsTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def test_get_custom_settings(self):
        self.assertEqual(settings.CBRF_APP_NAME, 'test_app')
        self.assertEqual(settings.DAYS_FOR_POPULATE, 30)
        self.assertIn('custom_field', Currency.__dict__)
        self.assertIn('custom_field', Record.__dict__)
