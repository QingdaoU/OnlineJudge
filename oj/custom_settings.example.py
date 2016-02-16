# coding=utf-8
import os

# please set your own SECRET_KEY to a long random string
SECRET_KEY = None


SSO = {"callback": "https://xxxxxxxxx/login"}

WEBSITE_INFO = {"website_name": u"xx大学 OnlineJudge",
                "website_name_shortcut": u"qduoj",
                "website_footer": u"xx大学xx学院<a href=\"http://www.miibeian.gov.cn/\">京ICP备xxxxx号-1</a>",
                "url": u"https://your-domain.com"}


SMTP_CONFIG = {"smtp_server": "smtp.xxx.com",
               "email": "noreply@xxx.com",
               "password": os.environ.get("smtp_password", "111111"),
               "tls": False}
