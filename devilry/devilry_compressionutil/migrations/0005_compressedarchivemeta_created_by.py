# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-21 15:06
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('devilry_compressionutil', '0004_auto_20170120_1733'),
    ]

    operations = [
        migrations.AddField(
            model_name='compressedarchivemeta',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
