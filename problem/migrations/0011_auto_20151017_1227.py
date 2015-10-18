# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0010_auto_20151017_1226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='hint',
            field=utils.models.RichTextField(null=True, blank=True),
        ),
    ]
