# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import datetime

from django.apps import apps

from .settings import CBRF_APP_NAME

get_model = apps.get_model


def get_cbrf_model(model_name, *args, **kwargs):
    """
       Returns currency model, either default either customised, depending on
       ``settings.CBRF_APP_NAME``.
    """
    return get_model(CBRF_APP_NAME, model_name, *args, **kwargs)


def get_currency_rate(currency: str = 'RUR') -> float:
    Currency = get_cbrf_model('Currency')
    Record = get_cbrf_model('Record')
    rate = 1
    if currency != "RUR":
        currency_obj = Currency.get_by_iso_char_code(currency)
        rate_record = Record.get_for_date(currency=currency_obj, date=datetime.date.today())
        if not rate_record:
            # берем последний курс
            rate_record = Record.objects.filter(currency=currency_obj, date__lte=datetime.date.today()).order_by("-date").first()
        rate = rate_record.value
    return rate
