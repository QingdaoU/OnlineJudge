# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_remove_user_problems_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='problems_status',
            field=models.TextField(default=b'{}'),
        ),
    ]
