from django.db import IntegrityError

from account.decorators import admin_role_required, ensure_created_by
from account.models import User
from utils.api import APIView, validate_serializer

from ..models import Group
from ..serializers import GroupSerializer, CreateGroupSerializer, EditGroupSerializer, DeleteGroupSerializer


class GroupAPI(APIView):
    @admin_role_required
    def get(self, request):
        _id = request.GET.get("id")
        keyword = request.GET.get("keyword")
        user = request.user
        if _id:
            try:
                group = Group.objects.get(id=_id)
                ensure_created_by(group, user)
                return self.success(GroupSerializer(group).data)
            except Group.DoesNotExist:
                return self.error("Group does not exist")
        groups = Group.objects.all().order_by("-create_time")
        if not user.is_super_admin():
            groups = groups.filter(created_by=user)
        if keyword:
            groups = groups.filter(name__contains=keyword)
        return self.success(self.paginate_data(request, groups, GroupSerializer))

    @validate_serializer(CreateGroupSerializer)
    def post(self, request):
        data = request.data
        data["created_by"] = request.user
        try:
            group = Group.objects.create(**data)
        except IntegrityError:
            return self.error("小组名不能重复")
        return self.success(GroupSerializer(group).data)

    @validate_serializer(EditGroupSerializer)
    def put(self, request):
        data = request.data
        _id = data.pop("id")
        try:
            group = Group.objects.get(id=_id)
        except Group.DoesNotExist:
            return self.error("Group does not exist")
        ensure_created_by(group, request.user)
        try:
            Group.objects.filter(id=_id).update(**data)
        except IntegrityError:
            return self.error("小组名不能重复")
        return self.success()

    @validate_serializer(DeleteGroupSerializer)
    def delete(self, request):
        data = request.data
        try:
            group = Group.objects.get(id=data["group_id"])
        except Group.DoesNotExist:
            return self.error("Group does not exist")
        ensure_created_by(group, request.user)
        if not data.get("user_id"):
            group.members.clear()
            group.delete()
            return self.success()
        else:
            group.members.remove(User.objects.get(id=data["user_id"]))
            return self.success(GroupSerializer(group).data)
