# coding=utf-8
from django.shortcuts import render
from django.http import HttpResponse

from account.models import User
from group.models import Group, UserGroupRelation, JoinGroupRequest


def install(request):
    for i in range(10):
        user = User.objects.create(username="root" + str(i), admin_type=2, real_name="real_name", email="11111@qq.com")
        user.set_password("root")
        user.save()
    for i in range(10):
        group = Group.objects.create(name="group" + str(i),
                                     description="description",
                                     admin=User.objects.get(username="root0"))
        for i in range(7):
            UserGroupRelation.objects.create(user=User.objects.get(username="root" + str(i)), group=group)
        for i in range(7, 10):
            JoinGroupRequest.objects.create(user=User.objects.get(username="root" + str(i)),
                                            group=group, message=u"你好啊")
    return HttpResponse("success")
