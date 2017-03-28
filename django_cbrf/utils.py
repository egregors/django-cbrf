# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.apps import apps

from .settings import CBRF_APP_NAME

get_model = apps.get_model


def get_cbrf_model(model_name, *args, **kwargs):
    """
       Returns currency model, either default either customised, depending on
       ``settings.CBRF_APP_NAME``.
    """
    return get_model(CBRF_APP_NAME, model_name, *args, **kwargs)
