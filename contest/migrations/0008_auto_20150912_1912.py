# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0007_contestsubmission_ac_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contest',
            old_name='show_rank',
            new_name='real_time_rank',
        ),
    ]
