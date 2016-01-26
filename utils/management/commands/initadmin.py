# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from account.models import User, SUPER_ADMIN, UserProfile
from utils.shortcuts import rand_str


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(username="root", real_name="root", email="root@oj.com", admin_type=SUPER_ADMIN)
        rand_password = rand_str(length=6)
        user.set_password(rand_password)
        user.save()
        UserProfile.objects.create(user=user)
        self.stdout.write("Successfully created super admin user.\nUsername: root\nPassword: %s\n"
                          "Remember to change password and turn on two factors auth "
                          "after installation." % rand_password)
