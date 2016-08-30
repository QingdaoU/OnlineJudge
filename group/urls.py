from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^groups/$', group_list_page, name="group_list_page"),
    url(r'^groups/(?P<page>\d+)/$', group_list_page, name="group_list_page"),
    url(r'^group/(?P<group_id>\d+)/$', group_page, name="group_page"),
    url(r'^group/(?P<group_id>\d+)/applications/$', application_list_page, name="group_application_page"),
    url(r'^group/application/(?P<request_id>\d+)/$', application_page, name="group_application"),
    url(r'^api/group_join/$', JoinGroupAPIView.as_view(), name="group_join_api"),
    url(r'^api/admin/group/$', GroupAdminAPIView.as_view(), name="group_admin_api"),
    url(r'^api/admin/group_member/$', GroupMemberAdminAPIView.as_view(), name="group_member_admin_api"),
    url(r'^api/admin/group/promot_as_admin/$', GroupPrometAdminAPIView.as_view(), name="group_promote_admin_api"),
    url(r'^api/admin/join_group_request/$', JoinGroupRequestAdminAPIView.as_view(),
        name="join_group_request_admin_api"),
]