# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-02-07 19:51
from __future__ import unicode_literals

import devilry.apps.core.models.custom_db_fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('devilry_group', '0026_datamigrate_update_for_no_none_values_in_feedbackset_deadline'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbacksetPassedPreviousPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assignment_short_name', devilry.apps.core.models.custom_db_fields.ShortNameField(help_text='Up to 20 letters of lowercase english letters (a-z), numbers, underscore ("_") and hyphen ("-"). Used when the name takes too much space.', max_length=20, verbose_name='Short name')),
                ('assignment_long_name', devilry.apps.core.models.custom_db_fields.LongNameField(db_index=True, max_length=100, verbose_name=b'Name')),
                ('assignment_max_points', models.PositiveIntegerField(default=0)),
                ('assignment_passing_grade_min_points', models.PositiveIntegerField(default=0)),
                ('period_short_name', devilry.apps.core.models.custom_db_fields.ShortNameField(help_text='Up to 20 letters of lowercase english letters (a-z), numbers, underscore ("_") and hyphen ("-"). Used when the name takes too much space.', max_length=20, verbose_name='Short name')),
                ('period_long_name', devilry.apps.core.models.custom_db_fields.LongNameField(db_index=True, max_length=100, verbose_name=b'Name')),
                ('period_start_time', models.DateTimeField()),
                ('period_end_time', models.DateField()),
                ('grading_points', models.PositiveIntegerField(default=0)),
                ('grading_published_datetime', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='feedbackset',
            name='deadline_datetime',
            field=models.DateTimeField(),
        ),
        migrations.AddField(
            model_name='feedbacksetpassedpreviousperiod',
            name='feedbackset',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='devilry_group.FeedbackSet'),
        ),
        migrations.AddField(
            model_name='feedbacksetpassedpreviousperiod',
            name='grading_published_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
