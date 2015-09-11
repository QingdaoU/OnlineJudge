# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0006_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='contestsubmission',
            name='ac_time',
            field=models.IntegerField(default=0),
        ),
    ]
