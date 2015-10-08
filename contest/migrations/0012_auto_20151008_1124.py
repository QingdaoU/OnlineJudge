# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0011_contestrank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contestrank',
            name='submission_info',
            field=jsonfield.fields.JSONField(default={}),
        ),
        migrations.AlterModelTable(
            name='contestrank',
            table='contest_rank',
        ),
    ]
