from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase

from django_cbrf.models import Currency


class CBRFManagementCommandsTestCase(TestCase):
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
