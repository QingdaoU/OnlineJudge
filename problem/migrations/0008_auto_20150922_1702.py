# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0007_remove_problem_last_update_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='description',
            field=utils.models.RichTextField(),
        ),
    ]
