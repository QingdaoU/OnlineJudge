from django.core.management.base import BaseCommand

from account.models import AdminType, User, UserProfile
from utils.shortcuts import rand_str  # NOQA


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            admin = User.objects.get(username="root")
            if admin.admin_type == AdminType.SUPER_ADMIN:
                self.stdout.write(self.style.WARNING("Super admin user 'root' already exists, "
                                                     "would you like to reset it's password?\n"
                                                     "Input yes to confirm: "))
                if input() == "yes":
                    # for dev
                    # rand_password = rand_str(length=6)
                    rand_password = "rootroot"
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
            user = User.objects.create(username="root", email="root@oj.com", admin_type=AdminType.SUPER_ADMIN)
            # for dev
            # rand_password = rand_str(length=6)
            rand_password = "rootroot"
            user.set_password(rand_password)
            user.save()
            UserProfile.objects.create(user=user, time_zone="Asia/Shanghai")
            self.stdout.write(self.style.SUCCESS("Successfully created super admin user.\n"
                                                 "Username: root\nPassword: %s\n"
                                                 "Remember to change password and turn on two factors auth "
                                                 "after installation." % rand_password))
