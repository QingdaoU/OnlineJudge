# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def delete_user_output(apps, schema_editor):
    Submission = apps.get_model("submission", "Submission")
    for item in Submission.objects.all():
        if "data" in item.info and isinstance(item.info["data"], list):
            for index in range(len(item.info["data"])):
                item.info["data"][index]["output"] = ""
            item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0008_submission_ip'),
    ]

    operations = [
        migrations.RunPython(delete_user_output, reverse_code=migrations.RunPython.noop)
    ]
