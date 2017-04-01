# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import logging

from django.core.management import BaseCommand
from django.db import IntegrityError

from django_cbrf.utils import get_cbrf_model

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """ Load currencies and retes from cbr.ru according settings
    """
    help = """
Download all currencies and save them in DB

To force populate use:

    manage.py load_currencies --force
    """

    def add_arguments(self, parser):
        parser.add_argument('-f', '--force', action='store_true', default=False,
                            help='Populate Currencies even they already exist')

    def handle(self, *args, **options):
        Currency = get_cbrf_model('Currency')

        force = options.get('force', False)

        if not force:
            try:
                Currency.populate()
            except IntegrityError:
                logger.error('Abort. Looks like Currencies already populated. '
                             'To force populate use "python manage.py load_currencies --force"')
                raise IntegrityError(
                    'Currencies already populated. '
                    'To force populate use "python manage.py load_currencies --force"'
                )
        else:
            Currency.populate(force=True)

        logger.info('Done. Currencies was populated.')
