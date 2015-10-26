# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import account.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_auto_20151012_1546'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('avatar', models.CharField(default=account.models._random_avatar, max_length=50)),
                ('blog', models.URLField(null=True, blank=True)),
                ('mood', models.CharField(max_length=200, null=True, blank=True)),
                ('hduoj_username', models.CharField(max_length=30, null=True, blank=True)),
                ('bestcoder_username', models.CharField(max_length=30, null=True, blank=True)),
                ('codeforces_username', models.CharField(max_length=30, null=True, blank=True)),
                ('rank', models.IntegerField(default=65535)),
                ('accepted_number', models.IntegerField(default=0)),
                ('submissions_number', models.IntegerField(default=0)),
                ('problems_status', jsonfield.fields.JSONField(default={})),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_profile',
            },
        ),
    ]
