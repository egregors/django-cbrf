# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import logging

from cbrf import get_currencies_info
from django.conf import settings
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

if settings.DEBUG:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
else:
    logging.disable(logging.CRITICAL)


class AbstractCurrency(models.Model):
    cbrf_id = models.CharField(verbose_name='CB RF code', max_length=12, unique=True, db_index=True)
    parent_code = models.CharField(verbose_name='parent code', max_length=6)

    name = models.CharField(verbose_name=_('name'), max_length=64)
    eng_name = models.CharField(verbose_name=_('english name'), max_length=64)
    denomination = models.SmallIntegerField(verbose_name=_('denomination'), default=1)
    iso_num_code = models.SmallIntegerField(verbose_name=_('ISO numeric code'), blank=True,
                                            null=True, default=None)
    iso_char_code = models.CharField(verbose_name=_('ISO char code'), max_length=3, blank=True,
                                     db_index=True, null=True, default=None)

    class Meta:
        abstract = True
        verbose_name = _('currency')
        verbose_name_plural = _('currencies')
        ordering = ('cbrf_id',)

    def __str__(self):
        return '[{}] {}/{}'.format(self.cbrf_id, self.name, self.eng_name)

    @classmethod
    def _populate(cls):
        """ Load list of Currencies from cbr.ru and save all.
        
        XML Elements -> models.Model
        
        <Valuta name="Foreign Currency Market Lib">
            <Item ID="R01500">
                <Name>Молдавский лей</Name>
                <EngName>Moldova Lei</EngName>
                <Nominal>10</Nominal>
                <ParentCode>R01500</ParentCode>
                <ISO_Num_Code>498</ISO_Num_Code>
                <ISO_Char_Code>MDL</ISO_Char_Code>
            </Item>
            <Item ID="R01235">
                <Name>Доллар США</Name>
                <EngName>US Dollar</EngName>
                <Nominal>1</Nominal>
                <ParentCode>R01235</ParentCode>
                <ISO_Num_Code>840</ISO_Num_Code>
                <ISO_Char_Code>USD</ISO_Char_Code>
            </Item>
        <...>
        
        """
        raw_currencies = get_currencies_info()
        for currency in raw_currencies:
            logger.info('{} ({}) populated'.format(currency.attrib['ID'], currency.findtext('EngName')))
            _iso_num_code = currency.findtext('ISO_Num_Code')
            _iso_char_code = currency.findtext('ISO_Char_Code')

            with transaction.atomic():
                cls.objects.create(
                    cbrf_id=currency.attrib['ID'],
                    parent_code=currency.findtext('ParentCode'),
                    name=currency.findtext('Name'),
                    eng_name=currency.findtext('EngName'),
                    denomination=int(currency.findtext('Nominal')),
                    iso_num_code=int(_iso_num_code) if _iso_num_code else None,
                    iso_char_code=_iso_char_code if _iso_char_code else None,
                )

    @classmethod
    def populate(cls):
        cls._populate()

    @classmethod
    def get_by_cbrf_id(cls, cbrf_id: str):
        try:
            return cls.objects.get(cbrf_id=cbrf_id)
        except cls.DoesNotExist:
            logger.error("Currency with {} code is not exist!".format(cbrf_id))
            return None

    @classmethod
    def get_by_iso_num_code(cls, iso_num_code: str or int):
        try:
            return cls.objects.get(iso_num_code=int(iso_num_code))
        except cls.DoesNotExist:
            logger.error("Currency with {} iso code is not exist!".format(iso_num_code))
            return None

    @classmethod
    def get_by_iso_char_code(cls, iso_char_code: str):
        try:
            return cls.objects.get(iso_char_code=iso_char_code)
        except cls.DoesNotExist:
            logger.error("Currency with {} iso code is not exist!".format(iso_char_code))
            return None
