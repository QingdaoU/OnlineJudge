# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0004_remove_submission_is_counted'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='contest_id',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
