# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-09 13:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_comment', '0008_commentfile_v2_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]