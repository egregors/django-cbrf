# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.core.management import BaseCommand


class Command(BaseCommand):
    """ Load currencies and retes from cbr.ru according settings
    """
    help = ''

    def handle(self, *args, **options):
        pass
