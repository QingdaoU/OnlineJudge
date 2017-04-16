#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _

from utils.api import APIView, validate_serializer

from ..decorators import login_required
from ..serializers import EditUserSerializer, UserSerializer


# class UserInfoAPI(APIView):
#     @login_required
#     def get(self, request):
#         """
#         Return user info api
#         """
#         return self.success(UserSerializer(request.user).data)


class UserProfileAPI(APIView):
    @login_required
    def get(self, request):
        """
        Return user info api
        """
        return self.success(UserSerializer(request.user).data)

    @validate_serializer(EditUserSerializer)
    @login_required
    def put(self, request):
        data = request.data
        user_profile = request.user.userprofile
        if data["avatar"]:
            user_profile.avatar = data["avatar"]
        else:
            user_profile.mood = data["mood"]
            user_profile.blog = data["blog"]
            user_profile.school = data["school"]
            user_profile.student_id = data["student_id"]
            user_profile.phone_number = data["phone_number"]
            user_profile.major = data["major"]
            # Timezone & language 暂时不加
        user_profile.save()
        return self.success(_("Succeeded"))


