# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_user_problems_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='problems_status',
            field=utils.models.JsonField(default={}),
        ),
    ]
