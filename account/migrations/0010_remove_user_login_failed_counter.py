# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_user_reset_password_token_create_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='login_failed_counter',
        ),
    ]
