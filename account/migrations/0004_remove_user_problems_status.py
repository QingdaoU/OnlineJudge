# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20150915_2025'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='problems_status',
        ),
    ]
