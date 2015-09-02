# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0004_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='joingrouprequest',
            name='accepted',
            field=models.BooleanField(default=False),
        ),
    ]
