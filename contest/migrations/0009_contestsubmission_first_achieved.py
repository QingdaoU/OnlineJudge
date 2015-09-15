# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0008_auto_20150912_1912'),
    ]

    operations = [
        migrations.AddField(
            model_name='contestsubmission',
            name='first_achieved',
            field=models.BooleanField(default=False),
        ),
    ]
