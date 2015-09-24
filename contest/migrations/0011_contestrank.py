# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import utils.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contest', '0010_auto_20150922_1703'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContestRank',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total_submission_number', models.IntegerField(default=0)),
                ('total_ac_number', models.IntegerField(default=0)),
                ('total_time', models.IntegerField(default=0)),
                ('submission_info', utils.models.JsonField(default={})),
                ('contest', models.ForeignKey(to='contest.Contest')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
