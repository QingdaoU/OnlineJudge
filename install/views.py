# coding=utf-8
from django.shortcuts import render
from django.http import HttpResponse

from account.models import User


def install(request):
    user = User.objects.create(username="root", admin_type=2)
    user.set_password("root")
    user.save()
    return HttpResponse("success")