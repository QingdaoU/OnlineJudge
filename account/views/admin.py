import os
import re
import xlsxwriter
from django.db.models import Q
from django.http import HttpResponse

from submission.models import Submission
from utils.api import APIView, validate_serializer
from utils.shortcuts import rand_str

from ..decorators import super_admin_required
from ..models import AdminType, ProblemPermission, User, UserProfile
from ..serializers import EditUserSerializer, UserSerializer, GenerateUserSerializer
from ..serializers import ImportUserSeralizer


class UserAdminAPI(APIView):
    @validate_serializer(ImportUserSeralizer)
    @super_admin_required
    def post(self, request):
        data = request.data["users"]
        omitted_count = created_count = get_count = 0
        for user_data in data:
            if len(user_data) != 3 or len(user_data[0]) > 32:
                omitted_count += 1
                continue
            user, created = User.objects.get_or_create(username=user_data[0])
            user.set_password(user_data[1])
            user.email = user_data[2]
            user.save()
            if created:
                UserProfile.objects.create(user=user)
                created_count += 1
            else:
                get_count += 1
        return self.success({
            "omitted_count": omitted_count,
            "created_count": created_count,
            "get_count": get_count
        })

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
            user = user.filter(Q(username__icontains=keyword) |
                               Q(userprofile__real_name__icontains=keyword) |
                               Q(email__icontains=keyword))
        return self.success(self.paginate_data(request, user, UserSerializer))

    def delete_one(self, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return f"User {user_id} does not exist"
        profile = user.userprofile
        if profile.submission_number:
            return f"Can't delete the user {user_id} as he/she has submissions"
        user.delete()

    @super_admin_required
    def delete(self, request):
        id = request.GET.get("id")
        if not id:
            return self.error("Invalid Parameter, user_id is required")
        for user_id in id.split(","):
            if user_id:
                error = self.delete_one(user_id)
                if error:
                    return self.error(error)
        return self.success()


class GenerateUserAPI(APIView):
    @super_admin_required
    def get(self, request):
        """
        download users excel
        """
        file_id = request.GET.get("file_id")
        if not file_id:
            return self.error("Invalid Parameter, file_id is required")
        if not re.match(r"[a-zA-Z0-9]+", file_id):
            return self.error("Illegal file_id")
        file_path = f"/tmp/{file_id}.xlsx"
        if not os.path.isfile(file_path):
            return self.error("File does not exist")
        with open(file_path, "rb") as f:
            raw_data = f.read()
        os.remove(file_path)
        response = HttpResponse(raw_data)
        response["Content-Disposition"] = f"attachment; filename=users.xlsx"
        response["Content-Type"] = "application/xlsx"
        return response

    @validate_serializer(GenerateUserSerializer)
    @super_admin_required
    def post(self, request):
        data = request.data
        number_max_length = max(len(str(data["number_from"])), len(str(data["number_to"])))
        if number_max_length + len(data["prefix"]) + len(data["suffix"]) > 32:
            return self.error("Username should not more than 32 characters")
        if data["number_from"] > data["number_to"]:
            return self.error("Start number must be lower than end number")

        password_length = data.get("password_length", 8)
        default_email = data.get("default_email")

        file_id = rand_str(8)
        filename = f"/tmp/{file_id}.xlsx"
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        worksheet.set_column("A:B", 20)
        worksheet.write("A1", "Username")
        worksheet.write("B1", "Password")
        i = 1
        created_count = 0
        get_count = 0
        for number in range(data["number_from"], data["number_to"] + 1):
            username = f"{data['prefix']}{number}{data['suffix']}"
            password = rand_str(password_length)
            user, created = User.objects.get_or_create(username=username)
            user.email = default_email
            user.set_password(password)
            user.save()
            if created:
                UserProfile.objects.create(user=user)
                created_count += 1
            else:
                get_count += 1
            worksheet.write_string(i, 0, username)
            worksheet.write_string(i, 1, password)
            i += 1
        workbook.close()
        return self.success({
            "file_id": file_id,
            "created_count": created_count,
            "get_count": get_count
        })
