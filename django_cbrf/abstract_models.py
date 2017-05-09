# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import datetime
import logging
from decimal import Decimal

from cbrf import get_currencies_info, get_dynamic_rates, get_daily_rates
from cbrf.utils import str_to_date
from django.db import models, transaction, IntegrityError
from django.utils.translation import ugettext_lazy as _

from django_cbrf.utils import get_cbrf_model
from .settings import CBRF_APP_NAME

logger = logging.getLogger(__name__)


class AbstractCurrency(models.Model):
    """ Abstract Currency model """
    cbrf_id = models.CharField(verbose_name='CB RF code', max_length=12, unique=True, db_index=True)
    parent_code = models.CharField(verbose_name='parent code', max_length=6)

    name = models.CharField(verbose_name=_('name'), max_length=64)
    eng_name = models.CharField(verbose_name=_('english name'), max_length=64)
    denomination = models.IntegerField(verbose_name=_('denomination'), default=1)
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
        return '[{}] {}/{}'.format(self.iso_char_code, self.name, self.eng_name)

    @classmethod
    def _populate(cls, force: bool = False):
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
            _iso_num_code = currency.findtext('ISO_Num_Code')
            _iso_char_code = currency.findtext('ISO_Char_Code')

            try:
                with transaction.atomic():
                    cls.objects.create(
                        cbrf_id=currency.attrib['ID'],
                        parent_code=currency.findtext('ParentCode').replace(' ', ''),
                        name=currency.findtext('Name'),
                        eng_name=currency.findtext('EngName'),
                        denomination=int(currency.findtext('Nominal')),
                        iso_num_code=int(_iso_num_code) if _iso_num_code else None,
                        iso_char_code=_iso_char_code if _iso_char_code else None,
                    )
            except IntegrityError as err:
                if force:
                    logger.warning('{} with id: {} is already populated. Skipping.'.format(
                        currency.findtext('EngName'),
                        currency.attrib['ID'])
                    )
                else:
                    raise err

    @classmethod
    def populate(cls, force: bool = False):
        cls._populate(force=force)

    @classmethod
    def get_by_cbrf_id(cls, cbrf_id: str):
        try:
            return cls.objects.get(cbrf_id=cbrf_id)
        except cls.DoesNotExist:
            logger.error("Currency with {} code is not exist!".format(cbrf_id))
            logger.warning("You could use 'python manage.py load_currencies' to populate local db.")
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


class AbstractRecord(models.Model):
    """ Abstract Record model """
    currency = models.ForeignKey(CBRF_APP_NAME + '.Currency', on_delete=models.CASCADE,
                                 related_name="%(app_label)s_%(class)s")
    date = models.DateField()
    value = models.DecimalField(verbose_name=_('value'), max_digits=9, decimal_places=4)

    class Meta:
        abstract = True
        verbose_name = _('record')
        verbose_name_plural = _('records')
        unique_together = ('date', 'currency')

    def __str__(self):
        return '[{}] {}: {}'.format(self.currency.iso_char_code, self.date, self.value)

    @classmethod
    def _populate_for_date(cls, currency: AbstractCurrency, date: datetime.datetime = None):

        raw_rates = get_daily_rates(date)
        record = [rate for rate in raw_rates if rate.attrib['ID'] == currency.cbrf_id]

        if record:
            actual_date = str_to_date(raw_rates.attrib['Date'])
            rate = record[0]
            with transaction.atomic():
                try:
                    return cls.objects.create(
                        currency=currency,
                        date=actual_date.date(),
                        value=Decimal(rate.findtext('Value').replace(',', '.'))
                    )
                except IntegrityError:
                    logger.warning("Rate {} for {} already in db. Skipped.".format(
                        currency.eng_name, actual_date))
                    return

        raise ValueError("Error in parameters")

    @classmethod
    def _populate_for_dates(cls, date_begin: datetime.datetime, date_end: datetime.datetime,
                            currency: AbstractCurrency):
        """ Load list of currency rates from date_begin to date_end.
        
        :param date_begin: first day of rates
        :param date_end: last day of rates
        :param currency: see :class Currency:
        """
        raw_rates = get_dynamic_rates(date_req1=date_begin, date_req2=date_end, currency_id=currency.cbrf_id)

        for rate in raw_rates:
            with transaction.atomic():
                try:
                    cls.objects.create(
                        currency=currency,
                        date=str_to_date(rate.attrib['Date']).date(),
                        value=Decimal(rate.findtext('Value').replace(',', '.'))
                    )
                except IntegrityError:
                    logger.warning("Rate {} for {} already in db. Skipped.".format(
                        currency.eng_name, str_to_date(rate.attrib['Date'])))

        return cls.objects.filter(currency=currency, date__gte=date_begin, date__lte=date_end)

    @classmethod
    def populate_for_date(cls, currency: AbstractCurrency, date: datetime.datetime = None):
        return cls._populate_for_date(currency, date)

    @classmethod
    def populate_for_dates(cls, date_begin: datetime.datetime, date_end: datetime.datetime,
                           currency: AbstractCurrency):
        cls._populate_for_dates(date_begin, date_end, currency)

    @classmethod
    def get_for_date(cls, currency: AbstractCurrency, date: datetime.datetime = None, force: bool = False):

        currency = get_cbrf_model('Currency').objects.get(cbrf_id=currency.cbrf_id)
        if force:
            rate = cls._populate_for_date(currency, date)
        else:
            rate = cls.objects.filter(currency=currency, date=date).all()
            rate = rate.first() if rate else cls._populate_for_date(currency, date)

        return rate

    @classmethod
    def get_for_dates(cls, date_begin: datetime.datetime,
                      date_end: datetime.datetime, currency: AbstractCurrency,
                      force: bool = False):
        """ Try to get rates from local DB. If response is empty -> try to get from CBR API """

        currency = get_cbrf_model('Currency').objects.get(cbrf_id=currency.cbrf_id)

        if force:
            rates = cls._populate_for_dates(date_begin, date_end, currency)
        else:
            rates = cls.objects.filter(
                currency=currency,
                date__gte=date_begin,
                date__lte=date_end)
            if not rates:
                rates = cls._populate_for_dates(date_begin, date_end, currency)

        return rates
