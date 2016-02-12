# coding=utf-8
from django.core.management.base import BaseCommand
from account.models import User, SUPER_ADMIN, UserProfile
from utils.shortcuts import rand_str


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            admin = User.objects.get(username="root")
            if admin.admin_type == SUPER_ADMIN:
                self.stdout.write(self.style.WARNING("Super admin user 'root' already exists, "
                                                     "would you like to reset it's password?\n"
                                                     "Input yes to confirm: "))
                if raw_input() == "yes":
                    rand_password = rand_str(length=6)
                    admin.set_password(rand_password)
                    admin.save()
                    self.stdout.write(self.style.SUCCESS("Successfully created super admin user password.\n"
                                                         "Username: root\nPassword: %s\n"
                                                         "Remember to change password and turn on two factors auth "
                                                         "after installation." % rand_password))
                else:
                    self.stdout.write(self.style.SUCCESS("Nothing happened"))
            else:
                self.stdout.write(self.style.ERROR("User 'root' is not super admin."))
        except User.DoesNotExist:
            user = User.objects.create(username="root", real_name="root", email="root@oj.com", admin_type=SUPER_ADMIN)
            rand_password = rand_str(length=6)
            user.set_password(rand_password)
            user.save()
            UserProfile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS("Successfully created super admin user.\n"
                                                 "Username: root\nPassword: %s\n"
                                                 "Remember to change password and turn on two factors auth "
                                                 "after installation." % rand_password))
