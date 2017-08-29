import time
import pytz

from django.contrib import auth
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

from utils.api import JSONResponse


class SessionSecurityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated() and request.user.is_admin_role():
            if "last_activity" in request.session:
                # 24 hours passed since last visit
                if time.time() - request.session["last_activity"] >= 24 * 60 * 60:
                    auth.logout(request)
                    return JSONResponse.response({"error": "login-required", "data": _("Please login in first")})
            # update last active time
            request.session["last_activity"] = time.time()


class AdminRoleRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path_info
        if path.startswith("/admin/") or path.startswith("/api/admin/"):
            if not (request.user.is_authenticated() and request.user.is_admin_role()):
                return JSONResponse.response({"error": "login-required", "data": _("Please login in first")})


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated():
            timezone.activate(pytz.timezone(request.user.userprofile.time_zone))


class LogSqlMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        print("\033[94m", "#" * 30, "\033[0m")
        time_threshold = 0.03
        for query in connection.queries:
            if float(query["time"]) > time_threshold:
                print("\033[93m", query, "\n", "-" * 30, "\033[0m")
            else:
                print(query, "\n", "-" * 30)
        return response
