# coding=utf-8
from __future__ import unicode_literals

from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q
from django.utils.translation import ugettext as _
from rest_framework.views import APIView

from utils.shortcuts import (serializer_invalid_response, error_response,
                             success_response, paginate, rand_str)
from ..decorators import super_admin_required
from ..models import User, AdminType
from ..serializers import (UserSerializer, EditUserSerializer)


class UserAdminAPIView(APIView):
    @super_admin_required
    def put(self, request):
        """
        Edit user api
        """
        serializer = EditUserSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                user = User.objects.get(id=data["id"])
            except User.DoesNotExist:
                return error_response(_("User does not exist"))
            try:
                user = User.objects.get(username=data["username"])
                if user.id != data["id"]:
                    return error_response(_("Username already exists"))
            except User.DoesNotExist:
                pass

            try:
                user = User.objects.get(email=data["email"])
                if user.id != data["id"]:
                    return error_response(_("Email already exists"))
            # Some old data has duplicate email
            except MultipleObjectsReturned:
                return error_response(_("Email already exists"))
            except User.DoesNotExist:
                pass

            user.username = data["username"]
            user.real_name = data["real_name"]
            user.email = data["email"]
            user.admin_type = data["admin_type"]
            user.is_disabled = data["is_disabled"]

            if data["password"]:
                user.set_password(data["password"])

            if data["open_api"]:
                # Avoid reset user appkey after saving changes
                if not user.open_api:
                    user.open_api_appkey = rand_str()
            else:
                user.open_api_appkey = None
            user.open_api = data["open_api"]

            if data["two_factor_auth"]:
                # Avoid reset user tfa_token after saving changes
                if not user.two_factor_auth:
                    user.tfa_token = rand_str()
            else:
                user.tfa_token = None
            user.two_factor_auth = data["two_factor_auth"]

            if data["admin_type"] == AdminType.ADMIN:
                user.admin_extra_permission = list(set(data["admin_extra_permission"]))
            else:
                user.admin_extra_permission = []

            user.save()
            return success_response(UserSerializer(user).data)
        else:
            return serializer_invalid_response(serializer)

    @super_admin_required
    def get(self, request):
        """
        User list api / Get user by id
        """
        user_id = request.GET.get("user_id")
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return error_response(_("User does not exist"))
            return success_response(UserSerializer(user).data)

        user = User.objects.all().order_by("-create_time")

        admin_type = request.GET.get("admin_type", None)
        if admin_type:
            try:
                user = user.filter(admin_type__gte=int(admin_type))
            except ValueError:
                return error_response(_("Invalid parameter"))
        keyword = request.GET.get("keyword", None)
        if keyword:
            user = user.filter(Q(username__contains=keyword) |
                               Q(real_name__contains=keyword) |
                               Q(email__contains=keyword))
        return paginate(request, user, UserSerializer)
