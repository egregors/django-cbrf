import logging

from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase

from django_cbrf.models import Currency


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


class CurrencyTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        Currency.populate()

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
