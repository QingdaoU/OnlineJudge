# coding=utf-8
from django.conf.urls import include, url
from django.views.generic import TemplateView

urlpatterns = [
    url(r'', include('account.urls')),
    url(r'', include('group.urls')),
    url(r'', include('contest.urls')),
    url(r'', include('problem.urls')),
    url(r'', include('submission.urls')),
    url(r'', include('utils.urls')),
    url(r'', include('announcement.urls')),
    url(r'', include('judge_dispatcher.urls')),

    url(r'^about/$', TemplateView.as_view(template_name="utils/about.html"), name="about_page"),
    url(r'^help/$', TemplateView.as_view(template_name="utils/help.html"), name="help_page"),
]
