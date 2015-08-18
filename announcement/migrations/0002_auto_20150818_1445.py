# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0004_merge'),
        ('announcement', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='groups',
            field=models.ManyToManyField(to='group.Group'),
        ),
        migrations.AddField(
            model_name='announcement',
            name='is_global',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
