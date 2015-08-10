# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('sample', models.TextField(blank=True)),
                ('test_case_id', models.CharField(max_length=40)),
                ('hint', models.TextField(null=True, blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('last_update_time', models.DateTimeField(auto_now=True)),
                ('source', models.CharField(max_length=30, null=True, blank=True)),
                ('time_limit', models.IntegerField()),
                ('memory_limit', models.IntegerField()),
                ('visible', models.BooleanField(default=True)),
                ('total_submit_number', models.IntegerField(default=0)),
                ('total_accepted_number', models.IntegerField(default=0)),
                ('difficulty', models.IntegerField()),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProblemTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'problem_tag',
            },
        ),
        migrations.AddField(
            model_name='problem',
            name='tags',
            field=models.ManyToManyField(to='problem.ProblemTag', null=True),
        ),
    ]
