# coding=utf-8

from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            if os.system("python manage.py migrate") != 0:
                self.stdout.write(self.style.ERROR("Failed to execute command 'migrate'"))
                exit(1)
            if os.system("python manage.py migrate --database=submission") != 0:
                self.stdout.write(self.style.ERROR("Failed to execute command 'migrate --database=submission'"))
                exit(1)
            if os.system("python manage.py initadmin") != 0:
                self.stdout.write(self.style.ERROR("Failed to execute command 'initadmin'"))
                exit(1)
            self.stdout.write(self.style.SUCCESS("Done"))
        except Exception as e:
            self.stdout.write(self.style.ERROR("Failed to initialize, error: " + str(e)))
