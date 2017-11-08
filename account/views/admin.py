from django.db.models import Q

from submission.models import Submission
from utils.api import APIView, validate_serializer
from utils.shortcuts import rand_str

from ..decorators import super_admin_required
from ..models import AdminType, ProblemPermission, User
from ..serializers import EditUserSerializer, UserSerializer


class UserAdminAPI(APIView):
    @validate_serializer(EditUserSerializer)
    @super_admin_required
    def put(self, request):
        """
        Edit user api
        """
        data = request.data
        try:
            user = User.objects.get(id=data["id"])
        except User.DoesNotExist:
            return self.error("User does not exist")
        if User.objects.filter(username=data["username"]).exclude(id=user.id).exists():
            return self.error("Username already exists")
        if User.objects.filter(email=data["email"].lower()).exclude(id=user.id).exists():
            return self.error("Email already exists")

        pre_username = user.username
        user.username = data["username"]
        user.email = data["email"]
        user.admin_type = data["admin_type"]
        user.is_disabled = data["is_disabled"]

        if data["admin_type"] == AdminType.ADMIN:
            user.problem_permission = data["problem_permission"]
        elif data["admin_type"] == AdminType.SUPER_ADMIN:
            user.problem_permission = ProblemPermission.ALL
        else:
            user.problem_permission = ProblemPermission.NONE

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

        user.save()
        if pre_username != user.username:
            Submission.objects.filter(username=pre_username).update(username=user.username)
        return self.success(UserSerializer(user).data)

    @super_admin_required
    def get(self, request):
        """
        User list api / Get user by id
        """
        user_id = request.GET.get("id")
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return self.error("User does not exist")
            return self.success(UserSerializer(user).data)

        user = User.objects.all().order_by("-create_time")

        keyword = request.GET.get("keyword", None)
        if keyword:
            user = user.filter(Q(username__contains=keyword) |
                               Q(real_name__contains=keyword) |
                               Q(email__contains=keyword))
        return self.success(self.paginate_data(request, user, UserSerializer))
