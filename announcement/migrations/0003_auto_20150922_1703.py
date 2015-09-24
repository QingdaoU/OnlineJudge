# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('announcement', '0002_auto_20150818_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='content',
            field=utils.models.RichTextField(),
        ),
    ]
