# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.db import models


class AbstractCurrency(models.Model):
    cbrf_id = models.CharField(verbose_name='CB RF code', max_length=6, unique=True, db_index=True)
    name = models.CharField(verbose_name=_('name'), max_length=64)
    eng_name = models.CharField(verbose_name=_('english name'), max_length=64)
    denomination = models.SmallIntegerField(verbose_name=_('denomination'), default=1)
    iso_num_code = models.SmallIntegerField(verbose_name=_('ISO numeric code'), blank=True,
                                            null=True, default=None)
    iso_char_code = models.CharField(max_length=3, unique=True, db_index=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '[{}] {}/{}'.format(self.cbrf_id, self.name, self.eng_name)

    @classmethod
    def _populate_all(cls, currencies_list: list):
        return currencies_list
