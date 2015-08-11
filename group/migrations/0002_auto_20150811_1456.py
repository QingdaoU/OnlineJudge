# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(unique=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='joingrouprequest',
            name='group',
            field=models.ForeignKey(to='group.Group'),
        ),
        migrations.AlterUniqueTogether(
            name='usergrouprelation',
            unique_together=set([('group', 'user')]),
        ),
    ]
