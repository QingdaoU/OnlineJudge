import time
from django.utils.translation import ugettext as _
from django.contrib import auth

from utils.api import JSONResponse
from .models import AdminType


class SessionSecurityMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated() and request.user.admin_type in [AdminType.ADMIN, AdminType.SUPER_ADMIN]:
            if "last_activity" in request.session:
                # 24 hours passed since last visit
                if time.time() - request.session["last_activity"] >= 24 * 60 * 60:
                    auth.logout(request)
                    return JSONResponse.response({"error": "login-required", "data": _("Please login in first")})
            # update last active time
            request.session["last_activity"] = time.time()


class AdminRequiredMiddleware(object):
    def process_request(self, request):
        path = request.path_info
        if path.startswith("/admin/") or path.startswith("/api/admin/"):
            if not(request.user.is_authenticated() and request.user.is_admin()):
                return JSONResponse.response({"error": "login-required", "data": _("Please login in first")})
