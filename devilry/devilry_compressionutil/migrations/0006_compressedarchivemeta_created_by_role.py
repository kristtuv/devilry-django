# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-09-24 10:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_compressionutil', '0005_compressedarchivemeta_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='compressedarchivemeta',
            name='created_by_role',
            field=models.CharField(choices=[(b'student', 'Student'), (b'examiner', 'Examiner'), (b'admin', 'Admin')], default=b'', max_length=255),
        ),
    ]
