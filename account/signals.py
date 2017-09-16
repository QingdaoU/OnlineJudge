from django.utils.timezone import now
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out


@receiver(user_logged_in)
def add_user_session(sender, request, user, **kwargs):
    request.session["ip"] = request.META.get("REMOTE_ADDR", "")
    request.session["user_agent"] = request.META.get("HTTP_USER_AGENT", "")
    request.session["last_login"] = now()
    if request.session.session_key not in user.session_keys:
        user.session_keys.append(request.session.session_key)
        user.save()


@receiver(user_logged_out)
def delete_user_session(sender, request, user, **kwargs):
    # user may be None
    if user and request.session.session_key in user.session_keys:
        user.session_keys.remove(request.session.session_key)
        user.save()
