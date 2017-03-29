from django.db import models

# Create your models here.
from django_cbrf.abstract_models import AbstractCurrency, AbstractRecord


class Currency(AbstractCurrency):
    custom_field = models.CharField(max_length=8)


class Record(AbstractRecord):
    custom_field = models.CharField(max_length=8)
