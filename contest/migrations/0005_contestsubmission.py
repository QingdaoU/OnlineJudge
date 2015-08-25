# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contest', '0004_remove_contestproblem_difficulty'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContestSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total_submission_number', models.IntegerField(default=1)),
                ('ac', models.BooleanField()),
                ('total_time', models.IntegerField(default=0)),
                ('contest', models.ForeignKey(to='contest.Contest')),
                ('problem', models.ForeignKey(to='contest.ContestProblem')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'contest_submission',
            },
        ),
    ]
