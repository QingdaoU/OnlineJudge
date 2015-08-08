# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import account.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('username', models.CharField(unique=True, max_length=30)),
                ('real_name', models.CharField(max_length=30, null=True, blank=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('admin_type', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'user',
            },
            managers=[
                ('objects', account.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AdminGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
    ]
