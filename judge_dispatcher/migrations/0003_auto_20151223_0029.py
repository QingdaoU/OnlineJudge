# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge_dispatcher', '0002_auto_20151207_2310'),
    ]

    operations = [
        migrations.AddField(
            model_name='judgeserver',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='judgeserver',
            name='name',
            field=models.CharField(default='judger', max_length=30),
            preserve_default=False,
        ),
    ]
