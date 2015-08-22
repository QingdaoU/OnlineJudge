# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('group', '0004_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=40)),
                ('description', models.TextField()),
                ('mode', models.IntegerField()),
                ('show_rank', models.BooleanField()),
                ('show_user_submission', models.BooleanField()),
                ('password', models.CharField(max_length=30, null=True, blank=True)),
                ('contest_type', models.IntegerField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('last_updated_time', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('groups', models.ManyToManyField(to='group.Group')),
            ],
            options={
                'db_table': 'contest',
            },
        ),
        migrations.CreateModel(
            name='ContestProblem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('input_description', models.CharField(max_length=10000)),
                ('output_description', models.CharField(max_length=10000)),
                ('samples', models.TextField(blank=True)),
                ('test_case_id', models.CharField(max_length=40)),
                ('hint', models.TextField(null=True, blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('time_limit', models.IntegerField()),
                ('memory_limit', models.IntegerField()),
                ('visible', models.BooleanField(default=True)),
                ('total_submit_number', models.IntegerField(default=0)),
                ('total_accepted_number', models.IntegerField(default=0)),
                ('sort_index', models.CharField(max_length=30)),
                ('contest', models.ForeignKey(to='contest.Contest')),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'contest_problem',
            },
        ),
        migrations.CreateModel(
            name='ContestProblemTestCase',
            fields=[
                ('id', models.CharField(max_length=40, serialize=False, primary_key=True, db_index=True)),
                ('score', models.IntegerField()),
                ('problem', models.ForeignKey(to='contest.ContestProblem')),
            ],
            options={
                'db_table': 'contest_problem_test_case',
            },
        ),
    ]
