# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0006_submission_shared'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='judge_end_time',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='judge_start_time',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
