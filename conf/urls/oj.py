from django.conf.urls import url

from ..views import WebsiteConfigAPI

urlpatterns = [
    url(r'^website$', WebsiteConfigAPI.as_view(), name="website_info_api"),
]
