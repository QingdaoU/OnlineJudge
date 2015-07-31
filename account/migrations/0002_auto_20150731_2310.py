# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import account.models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                (b'objects', account.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='real_name',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
    ]
