# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import Count


def fix_problem_count_bugs(apps, schema_editor):
    Submission = apps.get_model("submission", "Submission")
    Problem = apps.get_model("problem", "Problem")

    for item in Problem.objects.filter(contest__isnull=True):
        submissions = Submission.objects.filter(problem=item)
        item.submission_number = submissions.count()
        results_count = submissions.values('result').annotate(count=Count('result')).order_by('result')
        info = dict()
        item.accepted_number = 0
        for stat in results_count:
            result = stat["result"]
            if result == 0:
                item.accepted_number = stat["count"]
            info[str(result)] = stat["count"]
        item.statistic_info = info
        item.save(update_fields=["submission_number", "accepted_number", "statistic_info"])


class Migration(migrations.Migration):
    dependencies = [
        ('problem', '0010_problem_spj_compile_ok'),
    ]

    operations = [
        migrations.RunPython(fix_problem_count_bugs, reverse_code=migrations.RunPython.noop)
    ]
