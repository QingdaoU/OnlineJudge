# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import Count


def fix_rejudge_bugs(apps, schema_editor):
    Submission = apps.get_model("submission", "Submission")
    Problem = apps.get_model("problem", "Problem")
    User = apps.get_model("account", "User")

    for item in Problem.objects.filter(contest__isnull=True):
        submissions = Submission.objects.filter(problem=item)
        item.submission_number = submissions.count()
        results_count = submissions.annotate(count=Count('result')).values('result', 'count')
        for stat in results_count:
            if stat["result"] == 0:
                item.accepted_number = stat["count"]
            item.statistic_info[str(stat)] = stat["count"]
        item.save(update_fields=["submission_number", "accepted_number", "statistic_info"])

    for user in User.objects.all():
        submissions = Submission.objects.filter(user_id=user.id)
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
