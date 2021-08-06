from django.db.models import Q
from django.template.loader import render_to_string
from utils.api import APIView, validate_serializer
from utils.cache import cache
from utils.throttling import TokenBucket
from account.models import User
from account.decorators import login_required
from account.serializers import UserProfileSerializer
from options.options import SysOptions
from forum.models import ForumPost, ForumReply
from forum.serializers import (CreateEditForumPostSerializer, ForumPostSerializer,
                               CreateEditForumReplySerializer, ForumReplySerializer)
from account.tasks import send_email_async


class ForumPostAPI(APIView):
    def throttling(self, request, is_super_admin):
        # 超级管理员 的请求暂不做限制
        if is_super_admin:
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
        username = request.user.username
        is_super_admin = User.objects.get(username=str(username), is_disabled=False).is_super_admin()

        error = self.throttling(request, is_super_admin)
        if error:
            return self.error(error)

        allow_post = SysOptions.allow_forum_post
        if not allow_post:
            return self.error("Don't allow to post")

        data = request.data
        if data["id"] != -1:
            try:
                forumpost = ForumPost.objects.get(id=data.pop("id"))
                if str(username) != str(forumpost.author):
                    if not is_super_admin:
                        return self.error("Username doesn't match")
                if not is_super_admin:
                    if data["is_top"] or data["is_light"] or data["is_nice"]:
                        return self.error("User doesn't have permission")
                    permission = SysOptions.forum_sort[data["sort"] - 1]["permission"]
                    if permission == "Super Admin":
                        return self.error("User doesn't have permission")

            except ForumPost.DoesNotExist:
                return self.error("ForumPost does not exist")

            for k, v in data.items():
                setattr(forumpost, k, v)
            forumpost.save()

            return self.success(ForumPostSerializer(forumpost).data)

        if not is_super_admin:
            permission = SysOptions.forum_sort[data["sort"] - 1]["permission"]
            if permission == "Super Admin":
                return self.error("User doesn't have permission")

        forumpost = ForumPost.objects.create(title=data["title"],
                                             content=data["content"],
                                             sort=data["sort"],
                                             is_top=False,
                                             is_nice=False,
                                             is_light=False,
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
            is_super_admin = User.objects.get(username=str(username), is_disabled=False).is_super_admin()
            forumpost = ForumPost.objects.get(id=request.GET["forumpost_id"])
            if str(username) == str(forumpost.author):
                ForumPost.objects.filter(id=request.GET["forumpost_id"]).delete()
                ForumReply.objects.filter(fa_id=request.GET["forumpost_id"]).delete()
            elif is_super_admin:
                ForumPost.objects.filter(id=request.GET["forumpost_id"]).delete()
                ForumReply.objects.filter(fa_id=request.GET["forumpost_id"]).delete()
            else:
                return self.error("Username doesn't match")
        return self.success()


class ForumReplyAPI(APIView):
    def throttling(self, request, is_super_admin):
        # 超级管理员 的请求暂不做限制
        if is_super_admin:
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
        username = request.user.username
        is_super_admin = User.objects.get(username=str(username), is_disabled=False).is_super_admin()

        error = self.throttling(request, is_super_admin)
        if error:
            return self.error(error)

        allow_reply = SysOptions.allow_forum_reply
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
        data = ForumReplySerializer(forumreply).data

        try:
            user = User.objects.get(id=data["author"]["id"], is_disabled=False)
            userprofile = UserProfileSerializer(user.userprofile, show_real_name=False).data
            data["author"].update({"grade": userprofile["grade"], "title": userprofile["user"]["title"], "title_color": userprofile["user"]["title_color"]})
        except Exception:
            data["author"].update({"grade": 0, "title": None, "title_color": None})

        forumpost = ForumPostSerializer(ForumPost.objects.select_related("author").get(id=data["fa_id"])).data
        author = User.objects.get(username=forumpost["author"]["username"], is_disabled=False)
        render_data = {
            "username": author.username,
            "website_name": SysOptions.website_name,
            "title": forumpost["title"],
            "link": f"{SysOptions.website_base_url}/Forum/{data['fa_id']}"
        }
        email_html = render_to_string("reply_email.html", render_data)
        send_email_async.send(from_name=SysOptions.website_name_shortcut,
                              to_email=author.email,
                              to_name=author.username,
                              subject=f"Your Post recepted a reply",
                              content=email_html)
        return self.success(data)

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
            try:
                user = User.objects.get(id=data["results"][i]["author"]["id"], is_disabled=False)
                userprofile = UserProfileSerializer(user.userprofile, show_real_name=False).data
                data["results"][i]["author"].update({"grade": userprofile["grade"], "title": userprofile["user"]["title"], "title_color": userprofile["user"]["title_color"]})
            except Exception:
                data["results"][i]["author"].update({"grade": 0, "title": None, "title_color": None})
        return self.success(data)

    @login_required
    def delete(self, request):
        """
        delete ForumReply
        """
        if request.GET.get("id"):
            username = request.user.username
            is_super_admin = User.objects.get(username=str(username), is_disabled=False).is_super_admin()
            forumreply = ForumReply.objects.get(id=request.GET["id"])
            forumoost = ForumPost.objects.get(id=forumreply.fa_id)
            if str(username) == str(forumreply.author):
                ForumReply.objects.filter(id=request.GET["id"]).delete()
            elif str(username) == str(forumoost.author.username):
                ForumReply.objects.filter(id=request.GET["id"]).delete()
            elif is_super_admin:
                ForumReply.objects.filter(id=request.GET["id"]).delete()
            else:
                return self.error("Username doesn't match")
        return self.success()
