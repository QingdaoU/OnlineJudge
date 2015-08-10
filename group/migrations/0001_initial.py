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
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('description', models.TextField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('join_group_setting', models.IntegerField()),
                ('visible', models.BooleanField(default=True)),
                ('admin', models.ForeignKey(related_name='my_groups', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'group',
            },
        ),
        migrations.CreateModel(
            name='JoinGroupRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField(default=False)),
                ('group', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='my_join_group_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'join_group_request',
            },
        ),
        migrations.CreateModel(
            name='UserGroupRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('join_time', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(to='group.Group')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_group_relation',
            },
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='group.UserGroupRelation'),
        ),
    ]
