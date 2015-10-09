# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_auto_20150929_2320'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='login_failed_counter',
            field=models.IntegerField(default=0),
        ),
    ]
