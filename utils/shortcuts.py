import logging
import random

from django.utils.crypto import get_random_string
from envelopes import Envelope

from conf.models import SMTPConfig

logger = logging.getLogger(__name__)


def send_email(from_name, to_email, to_name, subject, content):
    smtp = SMTPConfig.objects.first()
    if not smtp:
        return
    envlope = Envelope(from_addr=(smtp.email, from_name),
                       to_addr=(to_email, to_name),
                       subject=subject,
                       html_body=content)
    try:
        envlope.send(smtp.server,
                     login=smtp.email,
                     password=smtp.password,
                     port=smtp.port,
                     tls=smtp.tls)
        return True
    except Exception as e:
        logger.exception(e)
        return False


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
    for k, v in kv_data.iteritems():
        if ignore_none is True and kv_data[k] is None:
            continue
        if query_string != "":
            query_string += "&"
        else:
            query_string = "?"
        query_string += (k + "=" + str(v))
    return query_string
