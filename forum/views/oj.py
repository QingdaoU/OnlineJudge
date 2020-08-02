from django.db.models import Q
from utils.api import APIView, validate_serializer
from utils.cache import cache
from utils.throttling import TokenBucket
from account.models import User
from account.decorators import login_required
from account.serializers import UserProfileSerializer
from options.models import SysOptions
from forum.models import ForumPost, ForumReply
from forum.serializers import (CreateEditForumPostSerializer, ForumPostSerializer,
                               CreateEditForumReplySerializer, ForumReplySerializer)


class ForumPostAPI(APIView):
    def throttling(self, request):
        # 使用 open_api 的请求暂不做限制
        auth_method = getattr(request, "auth_method", "")
        if auth_method == "api_key":
            return
        user_bucket = TokenBucket(key=str(request.user.username),
                                  redis_conn=cache,
                                  capacity=2,
                                  fill_rate=0.03,
                                  default_capacity=2)
        can_consume, wait = user_bucket.consume()
        if not can_consume:
            return "Please wait %d seconds" % (int(wait))

    @validate_serializer(CreateEditForumPostSerializer)
    @login_required
    def post(self, request):
        """
        publish ForumPost
        """

        error = self.throttling(request)
        if error:
            return self.error(error)

        allow_post = SysOptions.objects.get(key="allow_forum_post").value
        if not allow_post:
            return self.error("Don't allow to post")

        data = request.data
        if data["id"] != -1:
            try:
                forumpost = ForumPost.objects.get(id=data.pop("id"))
                username = request.user.username
                user = User.objects.get(username=str(username), is_disabled=False)
                admin_type = UserProfileSerializer(user.userprofile, show_real_name=False).data["user"]["admin_type"]
                if str(username) != str(forumpost.author):
                    if admin_type != "Super Admin":
                        return self.error("Username doesn't match")
                if admin_type != "Super Admin":
                    if data["is_top"] or data["is_light"] or data["is_nice"]:
                        return self.error("User doesn't have permission")
                    permission = SysOptions.objects.get(key="forum_sort").value[data["sort"] - 1]["permission"]
                    if permission == "Super Admin":
                        return self.error("User doesn't have permission")

            except ForumPost.DoesNotExist:
                return self.error("ForumPost does not exist")

            for k, v in data.items():
                setattr(forumpost, k, v)
            forumpost.save()

            return self.success(ForumPostSerializer(forumpost).data)

        forumpost = ForumPost.objects.create(title=data["title"],
                                             content=data["content"],
                                             sort=data["sort"],
                                             is_top=data["is_top"],
                                             is_nice=data["is_light"],
                                             is_light=data["is_light"],
                                             author=request.user)
        return self.success(ForumPostSerializer(forumpost).data)

    def get(self, request):
        """
        get ForumPost list / get one ForumPost
        """
        forumpost_id = request.GET.get("forumpost_id")
        if forumpost_id:
            try:
                forumpost = ForumPost.objects.select_related("author").get(id=forumpost_id)
                forumpost_data = ForumPostSerializer(forumpost).data
                return self.success(forumpost_data)
            except ForumPost.DoesNotExist:
                return self.error("ForumPost does not exist")

        limit = request.GET.get("limit")
        if not limit:
            return self.error("Limit is needed")

        forumposts = ForumPost.objects.select_related("author").filter().order_by("-is_top", "-create_time",)

        # 按照分区筛选
        sort = request.GET.get("sort")
        if sort:
            forumposts = forumposts.filter(sort=sort)

        # 搜索的情况
        keyword = request.GET.get("keyword", "").strip()
        if keyword:
            forumposts = forumposts.filter(Q(title__icontains=keyword) | Q(id__icontains=keyword))

        data = self.paginate_data(request, forumposts, ForumPostSerializer)
        return self.success(data)

    @login_required
    def delete(self, request):
        """
        delete ForumPost
        """
        if request.GET.get("forumpost_id"):
            username = request.user.username
            user = User.objects.get(username=str(username), is_disabled=False)
            admin_type = UserProfileSerializer(user.userprofile, show_real_name=False).data["user"]["admin_type"]
            forumpost = ForumPost.objects.get(id=request.GET["forumpost_id"])
            if str(username) == str(forumpost.author):
                ForumPost.objects.filter(id=request.GET["forumpost_id"]).delete()
                ForumReply.objects.filter(fa_id=request.GET["forumpost_id"]).delete()
            elif admin_type == "Super Admin":
                ForumPost.objects.filter(id=request.GET["forumpost_id"]).delete()
                ForumReply.objects.filter(fa_id=request.GET["forumpost_id"]).delete()
            else:
                return self.error("Username doesn't match")
        return self.success()


class ForumReplyAPI(APIView):
    def throttling(self, request):
        # 使用 open_api 的请求暂不做限制
        auth_method = getattr(request, "auth_method", "")
        if auth_method == "api_key":
            return
        user_bucket = TokenBucket(key=str(request.user.username),
                                  redis_conn=cache,
                                  capacity=2,
                                  fill_rate=0.03,
                                  default_capacity=2)
        can_consume, wait = user_bucket.consume()
        if not can_consume:
            return "Please wait %d seconds" % (int(wait))

    @validate_serializer(CreateEditForumReplySerializer)
    @login_required
    def post(self, request):
        """
        publish/edit ForumReply
        """
        error = self.throttling(request)
        if error:
            return self.error(error)

        allow_reply = SysOptions.objects.get(key="allow_forum_reply").value
        if not allow_reply:
            return self.error("Don't allow to reply")

        data = request.data
        if not data["content"]:
            return self.error("Reply can not be empty")

        forumreplys = ForumReply.objects.select_related("author").filter(fa_id=data["fa_id"]).order_by("-create_time",)
        # 判断楼层
        if forumreplys.exists():
            floor = forumreplys.values().first()["floor"] + 1
        else:
            floor = 0

        forumreply = ForumReply.objects.create(fa_id=data["fa_id"],
                                               content=data["content"],
                                               floor=floor,
                                               author=request.user)
        return self.success(ForumReplySerializer(forumreply).data)

    def get(self, request):
        """
        get ForumReply list / get one ForumReply
        """
        fa_id = request.GET.get("fa_id")
        if not fa_id:
            return self.error("fa_id is needed")

        limit = request.GET.get("limit")
        if not limit:
            return self.error("Limit is needed")

        forumreplys = ForumReply.objects.select_related("author").filter(fa_id=fa_id)

        data = self.paginate_data(request, forumreplys, ForumReplySerializer)
        for i in range(0, len(data["results"])):
            user = User.objects.get(username=data["results"][i]["author"]["username"], is_disabled=False)
            grade = UserProfileSerializer(user.userprofile, show_real_name=True).data["grade"]
            data["results"][i]["author"].update({"grade": grade})
        return self.success(data)

    @login_required
    def delete(self, request):
        """
        delete ForumReply
        """
        if request.GET.get("id"):
            username = request.user.username
            user = User.objects.get(username=str(username), is_disabled=False)
            admin_type = UserProfileSerializer(user.userprofile, show_real_name=False).data["user"]["admin_type"]
            forumreply = ForumReply.objects.get(id=request.GET["id"])
            if str(username) == str(forumreply.author):
                ForumReply.objects.filter(id=request.GET["id"]).delete()
            elif admin_type == "Super Admin":
                ForumReply.objects.filter(id=request.GET["id"]).delete()
            else:
                return self.error("Username doesn't match")
        return self.success()
