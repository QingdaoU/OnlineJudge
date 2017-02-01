from django.conf.urls import url
from .captcha.views import show_captcha

urlpatterns = [
    url(r'^captcha/$', show_captcha, name="show_captcha"),
]