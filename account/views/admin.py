from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q
from django.utils.translation import ugettext as _

from utils.api import APIView, validate_serializer
from utils.shortcuts import rand_str

from ..decorators import super_admin_required
from ..models import User
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
            return self.error(_("User does not exist"))
        try:
            user = User.objects.get(username=data["username"])
            if user.id != data["id"]:
                return self.error(_("Username already exists"))
        except User.DoesNotExist:
            pass

        try:
            user = User.objects.get(email=data["email"])
            if user.id != data["id"]:
                return self.error(_("Email already exists"))
        # Some old data has duplicate email
        except MultipleObjectsReturned:
            return self.error(_("Email already exists"))
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

        user.save()
        return self.success(UserSerializer(user).data)

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
                return self.error(_("User does not exist"))
            return self.success(UserSerializer(user).data)

        user = User.objects.all().order_by("-create_time")

        keyword = request.GET.get("keyword", None)
        if keyword:
            user = user.filter(Q(username__contains=keyword) |
                               Q(real_name__contains=keyword) |
                               Q(email__contains=keyword))
        return self.success(self.paginate_data(request, user, UserSerializer))
