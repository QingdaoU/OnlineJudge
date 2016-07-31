# coding=utf-8
import time
import json
import urllib

from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _
from django.contrib import auth

from .models import AdminType, User


# todo remove this
from django.contrib import auth

class SessionSecurityMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated() and request.user.admin_type in [AdminType.ADMIN, AdminType.SUPER_ADMIN]:
            if "last_activity" in request.session:
                # 24 hours passwd since last visit
                if time.time() - request.session["last_activity"] >= 24 * 60 * 60:
                    auth.logout(request)
                    if request.is_ajax():
                        return HttpResponse(json.dumps({"code": 1, "data": _("Please login in first")}),
                                            content_type="application/json")
                    else:
                        return HttpResponseRedirect("/login/?__from=" + urllib.quote(request.path))
            # 更新最后活动日期
            request.session["last_activity"] = time.time()
