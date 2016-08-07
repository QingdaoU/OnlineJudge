# coding=utf-8
import time
import json
import urllib

from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.contrib import auth

from utils.shortcuts import redirect_to_login
from .models import AdminType


class SessionSecurityMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated() and request.user.admin_type in [AdminType.ADMIN, AdminType.SUPER_ADMIN]:
            if "last_activity" in request.session:
                # 24 hours passed since last visit
                if time.time() - request.session["last_activity"] >= 24 * 60 * 60:
                    auth.logout(request)
                    if request.is_ajax():
                        return HttpResponse(json.dumps({"code": 1, "data": _("Please login in first")}),
                                            content_type="application/json")
                    else:
                        return redirect_to_login(request)
            # 更新最后活动日期
            request.session["last_activity"] = time.time()
