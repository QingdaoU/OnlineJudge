# coding=utf-8
import json

from django.http import HttpResponse, HttpResponseRedirect


class AdminRequiredMiddleware(object):
    def process_request(self, request):
        path = request.path_info
        if path.startswith("/admin/") or path.startswith("/api/admin/"):
            if not(request.user.is_authenticated() and request.user.admin_type):
                if request.is_ajax():
                    return HttpResponse(json.dumps({"code": 1, "data": u"请先登录"}),
                                        content_type="application/json")
                else:
                    return HttpResponseRedirect("/login/")