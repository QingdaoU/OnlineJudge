# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0009_contestsubmission_first_achieved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contest',
            name='description',
            field=utils.models.RichTextField(),
        ),
        migrations.AlterField(
            model_name='contestproblem',
            name='description',
            field=utils.models.RichTextField(),
        ),
    ]
