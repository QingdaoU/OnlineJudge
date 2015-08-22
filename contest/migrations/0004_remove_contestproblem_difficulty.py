# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0003_contestproblem_difficulty'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contestproblem',
            name='difficulty',
        ),
    ]
