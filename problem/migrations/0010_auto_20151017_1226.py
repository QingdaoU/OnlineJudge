# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0009_auto_20151008_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='last_update_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='problem',
            name='source',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
