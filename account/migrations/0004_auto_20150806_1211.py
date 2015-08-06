# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_user_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='admin_group',
        ),
        migrations.AddField(
            model_name='user',
            name='admin_type',
            field=models.IntegerField(default=0),
        ),
    ]
