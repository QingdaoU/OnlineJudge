# coding=utf-8
import time
import json
import urllib
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import auth
from .models import ADMIN


class SessionSecurityMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated() and request.user.admin_type >= ADMIN:
            if "last_activity" in request.session:
                # 24个小时没有活动
                if time.time() - request.session["last_activity"] >= 24 * 60 * 60:
                    auth.logout(request)
                    if request.is_ajax():
                        return HttpResponse(json.dumps({"code": 1, "data": u"请先登录"}),
                                            content_type="application/json")
                    else:
                        return HttpResponseRedirect("/login/?__from=" + urllib.quote(request.path))
            # 更新最后活动日期
            request.session["last_activity"] = time.time()
