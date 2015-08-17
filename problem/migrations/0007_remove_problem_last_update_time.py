# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0006_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problem',
            name='last_update_time',
        ),
    ]
