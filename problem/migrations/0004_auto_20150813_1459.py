# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0003_auto_20150810_2233'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='description_input',
            field=models.CharField(default='hello', max_length=10000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='problem',
            name='description_output',
            field=models.CharField(default='hello', max_length=10000),
            preserve_default=False,
        ),
    ]
