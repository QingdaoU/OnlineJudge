# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('announcement', '0003_auto_20150922_1703'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='announcement',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='announcement',
            name='is_global',
        ),
    ]
