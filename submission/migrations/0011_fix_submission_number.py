# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def fix_rejudge_bugs(apps, schema_editor):
    Submission = apps.get_model("submission", "Submission")
    User = apps.get_model("account", "User")

    for user in User.objects.all():
        submissions = Submission.objects.filter(user_id=user.id, contest__isnull=True)
        profile = user.userprofile
        profile.submission_number = submissions.count()
        profile.accepted_number = submissions.filter(result=0).count()
        profile.save(update_fields=["submission_number", "accepted_number"])


class Migration(migrations.Migration):
    dependencies = [
        ('submission', '0009_delete_user_output'),
    ]

    operations = [
        migrations.RunPython(fix_rejudge_bugs, reverse_code=migrations.RunPython.noop)
    ]
