from django.conf.urls import url

from ..views.oj import ForumPostAPI, ForumReplyAPI

urlpatterns = [
    url(r"^forumpost/?$", ForumPostAPI.as_view(), name="ForumPost_api"),
    url(r"^forumreply/?$", ForumReplyAPI.as_view(), name="ForumReply_api"),
]
