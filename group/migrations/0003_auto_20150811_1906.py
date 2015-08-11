# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0002_auto_20150811_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='join_group_setting',
            field=models.IntegerField(default=1),
        ),
    ]
