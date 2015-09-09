# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0005_submission_contest_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='shared',
            field=models.BooleanField(default=False),
        ),
    ]
