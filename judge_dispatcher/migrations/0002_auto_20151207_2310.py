# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge_dispatcher', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='judgewaitingqueue',
            name='memory_limit',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='judgewaitingqueue',
            name='test_case_id',
            field=models.CharField(default=1, max_length=40),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='judgewaitingqueue',
            name='time_limit',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
