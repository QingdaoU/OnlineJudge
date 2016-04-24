# coding=utf-8
from django.core.management.base import BaseCommand
from account.models import UserProfile
from submission.models import Submission


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Please wait a minute"))
        for profile in UserProfile.objects.all():
            submissions = Submission.objects.filter(user_id=profile.user.id)
            profile.submission_number = submissions.count()
            accepted_problem_number = len(set(Submission.objects.filter(user_id=profile.user.id, contest_id__isnull=True)\
                .values_list("problem_id", flat=True)))
            accepted_contest_problem_number = len(set(Submission.objects.filter(user_id=profile.user.id, contest_id__isnull=False)\
                .values_list("problem_id", flat=True)))
            profile.accepted_problem_number = accepted_problem_number + accepted_contest_problem_number
            profile.save()
        self.stdout.write(self.style.SUCCESS("Succeeded"))
