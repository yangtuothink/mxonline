# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2019-03-17 13:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseorg',
            name='image',
            field=models.ImageField(max_length=1000, upload_to='org/%Y/%m', verbose_name='缩略图'),
        ),
    ]
