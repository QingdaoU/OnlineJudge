# coding=utf-8
import shutil
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from problem.models import Problem
from contest.models import ContestProblem


class Command(BaseCommand):
    """
    清除测试用例文件夹中无用的测试用例
    """
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Please backup your test case dir firstly!"))
        problem_test_cases = [item.test_case_id for item in Problem.objects.all()]
        contest_problem_test_cases = [item.test_case_id for item in ContestProblem.objects.all()]

        test_cases = list(set(problem_test_cases + contest_problem_test_cases))
        test_cases_dir = os.listdir(settings.TEST_CASE_DIR)

        # 在 test_cases_dir 而不在 test_cases 中的
        dir_to_be_removed = list(set(test_cases_dir).difference(set(test_cases)))
        if dir_to_be_removed:
            self.stdout.write(self.style.ERROR("Following dirs will be removed: "))
            for item in dir_to_be_removed:
                self.stdout.write(self.style.WARNING(os.path.join(settings.TEST_CASE_DIR, item)))
            self.stdout.write(self.style.ERROR("Input yes to confirm: "))
            if raw_input() == "yes":
                for item in dir_to_be_removed:
                    shutil.rmtree(os.path.join(settings.TEST_CASE_DIR, item), ignore_errors=True)
                self.stdout.write(self.style.SUCCESS("Done"))
            else:
                self.stdout.write(self.style.SUCCESS("Nothing happened"))
        else:
            self.stdout.write(self.style.SUCCESS("Test case dir is clean, nothing to do"))
