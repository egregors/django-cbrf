# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-26 10:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cbrf_id', models.CharField(db_index=True, max_length=12, unique=True, verbose_name='CB RF code')),
                ('parent_code', models.CharField(max_length=6, verbose_name='parent code')),
                ('name', models.CharField(max_length=64, verbose_name='name')),
                ('eng_name', models.CharField(max_length=64, verbose_name='english name')),
                ('denomination', models.SmallIntegerField(default=1, verbose_name='denomination')),
                ('iso_num_code', models.SmallIntegerField(blank=True, default=None, null=True, verbose_name='ISO numeric code')),
                ('iso_char_code', models.CharField(blank=True, db_index=True, default=None, max_length=3, null=True, verbose_name='ISO char code')),
            ],
            options={
                'verbose_name': 'currency',
                'verbose_name_plural': 'currencies',
                'ordering': ('cbrf_id',),
                'abstract': False,
            },
        ),
    ]