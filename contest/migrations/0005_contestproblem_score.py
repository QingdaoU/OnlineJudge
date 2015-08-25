# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0004_remove_contestproblem_difficulty'),
    ]

    operations = [
        migrations.AddField(
            model_name='contestproblem',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
