from django import forms

from utils.api import DateTimeTZField, serializers

from .models import AdminType, ProblemPermission, User, UserProfile


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=30)
    tfa_code = serializers.CharField(min_length=6, max_length=6, required=False, allow_null=True)


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=30, min_length=6)
    email = serializers.EmailField(max_length=254)
    captcha = serializers.CharField(max_length=4, min_length=4)


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(max_length=30, min_length=6)
    captcha = serializers.CharField(max_length=4, min_length=4)


class UserSerializer(serializers.ModelSerializer):
    create_time = DateTimeTZField()
    last_login = DateTimeTZField()

    class Meta:
        model = User
        fields = ["id", "username", "real_name", "email", "admin_type", "problem_permission",
                  "create_time", "last_login", "two_factor_auth", "open_api", "is_disabled"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile


class UserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile


class EditUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=30)
    real_name = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=30, min_length=6, allow_blank=True, required=False, default=None)
    email = serializers.EmailField(max_length=254)
    admin_type = serializers.ChoiceField(choices=(AdminType.REGULAR_USER, AdminType.ADMIN, AdminType.SUPER_ADMIN))
    problem_permission = serializers.ChoiceField(choices=(ProblemPermission.NONE, ProblemPermission.OWN,
                                                          ProblemPermission.ALL))
    open_api = serializers.BooleanField()
    two_factor_auth = serializers.BooleanField()
    is_disabled = serializers.BooleanField()


class EditUserProfileSerializer(serializers.Serializer):
    avatar = serializers.CharField(max_length=100, allow_null=True, required=False)
    blog = serializers.URLField(allow_null=True, required=False)
    mood = serializers.CharField(max_length=200, allow_null=True, required=False)
    phone_number = serializers.CharField(max_length=15, allow_null=True, required=False, )
    school = serializers.CharField(max_length=200, allow_null=True, required=False)
    major = serializers.CharField(max_length=200, allow_null=True, required=False)
    student_id = serializers.CharField(max_length=15, allow_null=True, required=False)


class ApplyResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    captcha = serializers.CharField(max_length=4, min_length=4)


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(min_length=1, max_length=40)
    password = serializers.CharField(min_length=6, max_length=30)
    captcha = serializers.CharField(max_length=4, min_length=4)


class SSOSerializer(serializers.Serializer):
    appkey = serializers.CharField(max_length=35)
    token = serializers.CharField(max_length=40)


class TwoFactorAuthCodeSerializer(serializers.Serializer):
    code = serializers.IntegerField()


class AvatarUploadForm(forms.Form):
    file = forms.FileField()
