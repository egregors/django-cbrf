import decimal
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
        self.assertNotEqual(len(Currency.objects.all()), 0)
        currency_count = Currency.objects.count()

        with self.assertRaisesMessage(IntegrityError,
                                      'Currencies already populated. '
                                      'To force populate use "python manage.py '
                                      'load_currencies --force"'):
            call_command('load_currencies')

        Currency.objects.first().delete()
        self.assertEqual(len(Currency.objects.all()), currency_count - 1)

        call_command('load_currencies', '--force')
        self.assertEqual(len(Currency.objects.all()), currency_count)

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

    def test_populate_for_date(self):
        self.assertEqual(len(Record.objects.all()), 0)

        usd = Currency.objects.get(cbrf_id='R01235')

        date = datetime(2017, 2, 25)
        record = Record.populate_for_date(currency=usd, date=date)

        self.assertEqual(record.date, datetime(2017, 2, 23).date())
        self.assertEqual(record.value, Decimal('57.4762'))

    def test_populate_for_date_with_bad_parameters(self):
        date = datetime(1213, 2, 2).date()
        usd = Currency.objects.get(cbrf_id='R01235')

        with self.assertRaisesMessage(ValueError, "Error in parameters"):
            record = Record.populate_for_date(currency=usd, date=date)

    def test_get_for_date(self):
        usd = Currency.objects.get(cbrf_id='R01235')

        date = datetime(2015, 3, 12).date()
        record = Record.get_for_date(usd, date)
        self.assertEqual(record.date, date)
        self.assertEqual(record.value, Decimal('62.6797'))

        date_1, date_2 = datetime(2015, 3, 12).date(), datetime(2015, 3, 20).date()
        Record._populate_for_dates(date_1, date_2, usd)

        record = Record.get_for_date(usd, datetime(2015, 3, 17).date())
        self.assertEqual(record.value, Decimal('62.1497'))

    def test_get_for_dates(self):
        self.assertEqual(len(Record.objects.all()), 0)

        usd = Currency.objects.get(cbrf_id='R01235')

        date_1 = datetime(2001, 3, 2)
        date_2 = datetime(2001, 3, 14)

        Record.get_for_dates(date_1, date_2, usd)

        self.assertEqual(len(Record.objects.all()), 8)

    def test_get_latest(self):
        date = datetime(2022, 12, 31)
        usd = Currency.objects.get(cbrf_id='R01235')
        record = Record.get_latest_for_date(usd, False, date)  # check for selected date not weekend
        self.assertEqual(record.value, decimal.Decimal("70.3375"))

        date = datetime(2023, 1, 5)
        record = Record.get_latest_for_date(usd, False, date)  # takes last day before weekend/holiday
        self.assertEqual(record.value, decimal.Decimal("70.3375"))


class CustomSettingsTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def test_get_custom_settings(self):
        self.assertEqual(settings.CBRF_APP_NAME, 'test_app')
        self.assertEqual(settings.DAYS_FOR_POPULATE, 30)
        self.assertIn('custom_field', Currency.__dict__)
        self.assertIn('custom_field', Record.__dict__)
