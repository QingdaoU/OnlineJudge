import os
import re
import datetime
import random
from base64 import b64encode
from io import BytesIO

from django.utils.crypto import get_random_string
from django.core.mail import get_connection, EmailMessage
from email.utils import formataddr


def rand_str(length=32, type="lower_hex"):
    """
    生成指定长度的随机字符串或者数字, 可以用于密钥等安全场景
    :param length: 字符串或者数字的长度
    :param type: str 代表随机字符串，num 代表随机数字
    :return: 字符串
    """
    if type == "str":
        return get_random_string(length, allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
    elif type == "lower_str":
        return get_random_string(length, allowed_chars="abcdefghijklmnopqrstuvwxyz0123456789")
    elif type == "lower_hex":
        return random.choice("123456789abcdef") + get_random_string(length - 1, allowed_chars="0123456789abcdef")
    else:
        return random.choice("123456789") + get_random_string(length - 1, allowed_chars="0123456789")


def build_query_string(kv_data, ignore_none=True):
    # {"a": 1, "b": "test"} -> "?a=1&b=test"
    query_string = ""
    for k, v in kv_data.items():
        if ignore_none is True and kv_data[k] is None:
            continue
        if query_string != "":
            query_string += "&"
        else:
            query_string = "?"
        query_string += (k + "=" + str(v))
    return query_string


def img2base64(img):
    with BytesIO() as buf:
        img.save(buf, "gif")
        buf_str = buf.getvalue()
    img_prefix = "data:image/png;base64,"
    b64_str = img_prefix + b64encode(buf_str).decode("utf-8")
    return b64_str


def datetime2str(value, format="iso-8601"):
    if format.lower() == "iso-8601":
        value = value.isoformat()
        if value.endswith("+00:00"):
            value = value[:-6] + "Z"
        return value
    return value.strftime(format)


def timestamp2utcstr(value):
    return datetime.datetime.utcfromtimestamp(value).isoformat()


def natural_sort_key(s, _nsre=re.compile(r"(\d+)")):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]


def send_email(smtp_config, from_name, to_email, to_name, subject, content):
    conn = get_connection(host=smtp_config["server"],
                          port=smtp_config["port"],
                          username=smtp_config["email"],
                          password=smtp_config["password"],
                          use_tls=smtp_config["tls"])
    msg = EmailMessage(subject=subject,
                       body=content,
                       from_email=formataddr((from_name, smtp_config['email'])),
                       to=[formataddr((to_name, to_email))],
                       connection=conn)
    msg.content_subtype = "html"
    return msg.send()


def get_env(name, default=""):
    return os.environ.get(name, default)


def DRAMATIQ_WORKER_ARGS(time_limit=3600_000, max_retries=0, max_age=7200_000):
    return {"max_retries": max_retries, "time_limit": time_limit, "max_age": max_age}


def check_is_id(value):
    try:
        return int(value) > 0
    except Exception:
        return False
