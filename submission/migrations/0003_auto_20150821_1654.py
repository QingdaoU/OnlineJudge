# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0002_submission_is_counted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='problem_id',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='user_id',
            field=models.IntegerField(db_index=True),
        ),
    ]
