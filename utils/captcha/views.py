# coding=utf-8
from django.http import HttpResponse

from utils.captcha import Captcha


def show_captcha(request):
    return HttpResponse(Captcha(request).display(), content_type="image/gif")
