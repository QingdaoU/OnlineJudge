from django.conf.urls import url

from ..views import WebsiteConfigAPI, SMTPAPI

urlpatterns = [
    url(r'^smtp$', SMTPAPI.as_view(), name="smtp_admin_api"),
    url(r'^website$', WebsiteConfigAPI.as_view(), name="website_config_api"),
]
