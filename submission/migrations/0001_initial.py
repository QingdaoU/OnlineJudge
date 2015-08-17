# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import utils.shortcuts


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.CharField(default=utils.shortcuts.rand_str, max_length=32, serialize=False, primary_key=True, db_index=True)),
                ('user_id', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('result', models.IntegerField(default=8)),
                ('language', models.IntegerField()),
                ('code', models.TextField()),
                ('problem_id', models.IntegerField()),
                ('info', models.TextField(null=True, blank=True)),
                ('accepted_answer_time', models.IntegerField(null=True, blank=True)),
                ('accepted_answer_info', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'submission',
            },
        ),
    ]
