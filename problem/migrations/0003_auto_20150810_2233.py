# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0002_remove_problemtag_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='problem',
            old_name='sample',
            new_name='samples',
        ),
    ]
