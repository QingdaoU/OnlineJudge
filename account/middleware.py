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
        if request.user.is_authenticated():
            if "last_activity" in request.session and request.user.is_admin_role():
                # 24 hours passed since last visit, 86400 = 24 * 60 * 60
                if time.time() - request.session["last_activity"] >= 86400:
                    auth.logout(request)
                    return JSONResponse.response({"error": "login-required", "data": _("Please login in first")})
            request.session["last_activity"] = time.time()


class SessionRecordMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated():
            session = request.session
            ip = request.META.get("REMOTE_ADDR", "")
            user_agent = request.META.get("HTTP_USER_AGENT", "")
            _ip = session.setdefault("ip", ip)
            _user_agent = session.setdefault("user_agent", user_agent)
            if ip != _ip or user_agent != _user_agent:
                session.modified = True
            user_sessions = request.user.session_keys
            if request.session.session_key not in user_sessions:
                user_sessions.append(session.session_key)
                request.user.save()


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
