# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JudgeServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.GenericIPAddressField()),
                ('port', models.IntegerField()),
                ('max_instance_number', models.IntegerField()),
                ('left_instance_number', models.IntegerField()),
                ('workload', models.IntegerField(default=0)),
                ('token', models.CharField(max_length=30)),
                ('lock', models.BooleanField(default=False)),
                ('status', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'judge_server',
            },
        ),
        migrations.CreateModel(
            name='JudgeWaitingQueue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('submission_id', models.CharField(max_length=40)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'judge_waiting_queue',
            },
        ),
    ]
