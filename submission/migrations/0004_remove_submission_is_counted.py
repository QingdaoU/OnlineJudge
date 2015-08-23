# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0003_auto_20150821_1654'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submission',
            name='is_counted',
        ),
    ]
