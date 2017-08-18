from base64 import b64encode

from . import Captcha
from ..api import APIView


class CaptchaAPIView(APIView):
    def get(self, request):
        img_prefix = "data:image/png;base64,"
        img = img_prefix + b64encode(Captcha(request).get()).decode("utf-8")
        return self.success(img)
