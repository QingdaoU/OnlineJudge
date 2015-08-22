# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0002_contest_visible'),
    ]

    operations = [
        migrations.AddField(
            model_name='contestproblem',
            name='difficulty',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
