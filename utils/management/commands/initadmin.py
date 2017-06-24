# coding=utf-8
from django.core.management.base import BaseCommand
from account.models import User, SUPER_ADMIN, UserProfile


class Command(BaseCommand):
    def handle(self, *args, **options):
        if User.objects.exists():
            return
        user = User.objects.create(username="root", real_name="root", email="root@oj.com", admin_type=SUPER_ADMIN)
        user.set_password("password@root")
        user.save()
        UserProfile.objects.create(user=user)
