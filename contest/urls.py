from django.conf.urls import url
from .views import *
from django.views.generic import TemplateView

urlpatterns = [

    url(r'^contest/(?P<contest_id>\d+)/problem/(?P<contest_problem_id>\d+)/$', contest_problem_page,
        name="contest_problem_page"),
    url(r'^contest/(?P<contest_id>\d+)/problem/(?P<contest_problem_id>\d+)/submissions/$',
        contest_problem_my_submissions_list_page,
        name="contest_problem_my_submissions_list_page"),

    url(r'^contest/(?P<contest_id>\d+)/$', contest_page, name="contest_page"),
    url(r'^contest/(?P<contest_id>\d+)/problems/$', contest_problems_list_page,
        name="contest_problems_list_page"),
    url(r'^contest/(?P<contest_id>\d+)/submissions/$', contest_problem_submissions_list_page,
        name="contest_problem_submissions_list_page"),
    url(r'^contest/(?P<contest_id>\d+)/submissions/(?P<page>\d+)/$',
        contest_problem_submissions_list_page, name="contest_problem_submissions_list_page"),

    url(r'^contests/$', contest_list_page, name="contest_list_page"),
    url(r'^contests/(?P<page>\d+)/$', contest_list_page, name="contest_list_page"),
    url(r'^contest/(?P<contest_id>\d+)/rank/$', contest_rank_page, name="contest_rank_page"),

    url(r'^admin/contest/$', TemplateView.as_view(template_name="admin/contest/add_contest.html"),
        name="add_contest_page"),

    url(r'^api/admin/contest/$', ContestAdminAPIView.as_view(), name="contest_admin_api"),
    url(r'^api/admin/contest_problem/$', ContestProblemAdminAPIView.as_view(), name="contest_problem_admin_api"),
    url(r'^api/admin/contest_problem/public/', MakeContestProblemPublicAPIView.as_view(),
        name="make_contest_problem_public"),
    url(r'^api/contest/password/$', ContestPasswordVerifyAPIView.as_view(), name="contest_password_verify_api"),
    url(r'^api/contest/time/$', ContestTimeAPIView.as_view(), name="contest_time_api_view"),

]