from account.decorators import admin_role_required, ensure_created_by
from utils.api import APIView, validate_serializer

from ..models import Group
from ..serializers import GroupSerializer


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

    def post(self, request):
        pass

    def put(self, request):
        pass

    def delete(self, request):
        pass
