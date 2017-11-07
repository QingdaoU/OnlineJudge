import os
from account.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        if User.objects.exists():
            self.stdout.write(self.style.WARNING("Nothing happened\n"))
            return
        try:
            if os.system("python manage.py initadmin") != 0:
                self.stdout.write(self.style.ERROR("Failed to execute command 'initadmin'"))
                exit(1)
            self.stdout.write(self.style.SUCCESS("Done"))
        except Exception as e:
            self.stdout.write(self.style.ERROR("Failed to initialize, error: " + str(e)))
