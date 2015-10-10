# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_user_login_failed_counter'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reset_password_token_create_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
