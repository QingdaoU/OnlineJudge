from group.models import Group
from utils.api import APIView, validate_serializer
from ..serializers import SimpleGroupSerializer, JoinGroupSerializer


class GroupAPI(APIView):
    def get(self, request):
        groups = Group.objects.filter(allow_join=True).order_by("-id")
        for item in groups:
            item.me = item.members.filter(username=request.user.username).exists()
        return self.success(SimpleGroupSerializer(groups, many=True).data)

    @validate_serializer(JoinGroupSerializer)
    def post(self, request):
        data = request.data
        try:
            group = Group.objects.get(allow_join=True, name=data["group_name"])
        except Group.DoesNotExist:
            return self.error("小组不存在")
        if group.members.filter(username=request.user.username).exists():
            return self.error("你已经在小组中了")
        if group.password and group.password != data["password"]:
            return self.error("密码错误")
        group.members.add(request.user)
        return self.success()
