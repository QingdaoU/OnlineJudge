# coding=utf-8
from __future__ import unicode_literals

from django.db import models


class SMTPConfig(models.Model):
    server = models.CharField(max_length=128)
    port = models.IntegerField(default=25)
    email = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    tls = models.BooleanField()

    class Meta:
        db_table = "smtp_config"


class WebsiteConfig(models.Model):
    base_url = models.CharField(max_length=128, default=None)
    name = models.CharField(max_length=32, default="Online Judge")
    name_shortcut = models.CharField(max_length=32, default="oj")
    website_footer = models.TextField(default="Online Judge")
    # allow register
    allow_register = models.BooleanField(default=True)
    # submission list show all user's submission
    submission_list_show_all = models.BooleanField(default=False)

    class Meta:
        db_table = "website_config"

