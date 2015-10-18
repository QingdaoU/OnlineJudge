# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0012_auto_20151008_1124'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contestproblemtestcase',
            name='problem',
        ),
        migrations.RemoveField(
            model_name='contestsubmission',
            name='contest',
        ),
        migrations.RemoveField(
            model_name='contestsubmission',
            name='problem',
        ),
        migrations.RemoveField(
            model_name='contestsubmission',
            name='user',
        ),
        migrations.RemoveField(
            model_name='contest',
            name='mode',
        ),
        migrations.RemoveField(
            model_name='contest',
            name='show_user_submission',
        ),
        migrations.RemoveField(
            model_name='contestproblem',
            name='score',
        ),
        migrations.AddField(
            model_name='contestproblem',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contestproblem',
            name='last_update_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='contestproblem',
            name='hint',
            field=utils.models.RichTextField(null=True, blank=True),
        ),
        migrations.DeleteModel(
            name='ContestProblemTestCase',
        ),
        migrations.DeleteModel(
            name='ContestSubmission',
        ),
    ]
