import functools
import os
import threading
import time

from django.db import transaction, IntegrityError

from utils.shortcuts import rand_str
from judge.languages import languages
from .models import SysOptions as SysOptionsModel


class my_property:
    """
    在 metaclass 中使用，以实现：
    1. ttl = None，不缓存
    2. ttl is callable，条件缓存
    3. 缓存 ttl 秒
    """
    def __init__(self, func=None, fset=None, ttl=None):
        self.fset = fset
        self.local = threading.local()
        self.ttl = ttl
        self._check_ttl(ttl)
        self.func = func
        functools.update_wrapper(self, func)

    def _check_ttl(self, value):
        if value is None or callable(value):
            return
        return self._check_timeout(value)

    def _check_timeout(self, value):
        if not isinstance(value, int):
            raise ValueError(f"Invalid timeout type: {type(value)}")
        if value < 0:
            raise ValueError("Invalid timeout value, it must >= 0")

    def __get__(self, obj, cls):
        if obj is None:
            return self

        now = time.time()
        if self.ttl:
            if hasattr(self.local, "value"):
                value, expire_at = self.local.value
                if now < expire_at:
                    return value

            value = self.func(obj)

            # 如果定义了条件缓存, ttl 是一个函数，返回要缓存多久；返回 0 代表不要缓存
            if callable(self.ttl):
                # 而且条件缓存说不要缓存，那就直接返回，不要设置 local
                timeout = self.ttl(value)
                self._check_timeout(timeout)

                if timeout == 0:
                    return value
                elif timeout > 0:
                    self.local.value = (value, now + timeout)
            else:
                # ttl 是一个数字
                self.local.value = (value, now + self.ttl)
            return value
        else:
            return self.func(obj)

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)
        if hasattr(self.local, "value"):
            del self.local.value

    def setter(self, func):
        self.fset = func
        return self

    def __call__(self, func, *args, **kwargs) -> "my_property":
        if self.func is None:
            self.func = func
            functools.update_wrapper(self, func)
        return self


DEFAULT_SHORT_TTL = 2


def default_token():
    token = os.environ.get("JUDGE_SERVER_TOKEN")
    return token if token else rand_str()


class OptionKeys:
    website_base_url = "website_base_url"
    website_name = "website_name"
    website_name_shortcut = "website_name_shortcut"
    website_footer = "website_footer"
    allow_register = "allow_register"
    submission_list_show_all = "submission_list_show_all"
    smtp_config = "smtp_config"
    judge_server_token = "judge_server_token"
    throttling = "throttling"
    languages = "languages"


class OptionDefaultValue:
    website_base_url = "http://127.0.0.1"
    website_name = "Online Judge"
    website_name_shortcut = "oj"
    website_footer = "Online Judge Footer"
    allow_register = True
    submission_list_show_all = True
    smtp_config = {}
    judge_server_token = default_token
    throttling = {"ip": {"capacity": 100, "fill_rate": 0.1, "default_capacity": 50},
                  "user": {"capacity": 20, "fill_rate": 0.03, "default_capacity": 10}}
    languages = languages


class _SysOptionsMeta(type):
    @classmethod
    def _get_keys(cls):
        return [key for key in OptionKeys.__dict__ if not key.startswith("__")]

    @classmethod
    def _init_option(mcs):
        for item in mcs._get_keys():
            if not SysOptionsModel.objects.filter(key=item).exists():
                default_value = getattr(OptionDefaultValue, item)
                if callable(default_value):
                    default_value = default_value()
                try:
                    SysOptionsModel.objects.create(key=item, value=default_value)
                except IntegrityError:
                    pass

    @classmethod
    def _get_option(mcs, option_key):
        try:
            option = SysOptionsModel.objects.get(key=option_key)
            value = option.value
            return value
        except SysOptionsModel.DoesNotExist:
            mcs._init_option()
            return mcs._get_option(option_key)

    @classmethod
    def _set_option(mcs, option_key: str, option_value):
        try:
            with transaction.atomic():
                option = SysOptionsModel.objects.select_for_update().get(key=option_key)
                option.value = option_value
                option.save()
        except SysOptionsModel.DoesNotExist:
            mcs._init_option()
            mcs._set_option(option_key, option_value)

    @classmethod
    def _increment(mcs, option_key):
        try:
            with transaction.atomic():
                option = SysOptionsModel.objects.select_for_update().get(key=option_key)
                value = option.value + 1
                option.value = value
                option.save()
        except SysOptionsModel.DoesNotExist:
            mcs._init_option()
            return mcs._increment(option_key)

    @classmethod
    def set_options(mcs, options):
        for key, value in options:
            mcs._set_option(key, value)

    @classmethod
    def get_options(mcs, keys):
        result = {}
        for key in keys:
            result[key] = mcs._get_option(key)
        return result

    @my_property(ttl=DEFAULT_SHORT_TTL)
    def website_base_url(cls):
        return cls._get_option(OptionKeys.website_base_url)

    @website_base_url.setter
    def website_base_url(cls, value):
        cls._set_option(OptionKeys.website_base_url, value)

    @my_property(ttl=DEFAULT_SHORT_TTL)
    def website_name(cls):
        return cls._get_option(OptionKeys.website_name)

    @website_name.setter
    def website_name(cls, value):
        cls._set_option(OptionKeys.website_name, value)

    @my_property(ttl=DEFAULT_SHORT_TTL)
    def website_name_shortcut(cls):
        return cls._get_option(OptionKeys.website_name_shortcut)

    @website_name_shortcut.setter
    def website_name_shortcut(cls, value):
        cls._set_option(OptionKeys.website_name_shortcut, value)

    @my_property(ttl=DEFAULT_SHORT_TTL)
    def website_footer(cls):
        return cls._get_option(OptionKeys.website_footer)

    @website_footer.setter
    def website_footer(cls, value):
        cls._set_option(OptionKeys.website_footer, value)

    @my_property
    def allow_register(cls):
        return cls._get_option(OptionKeys.allow_register)

    @allow_register.setter
    def allow_register(cls, value):
        cls._set_option(OptionKeys.allow_register, value)

    @my_property(ttl=DEFAULT_SHORT_TTL)
    def submission_list_show_all(cls):
        return cls._get_option(OptionKeys.submission_list_show_all)

    @submission_list_show_all.setter
    def submission_list_show_all(cls, value):
        cls._set_option(OptionKeys.submission_list_show_all, value)

    @my_property
    def smtp_config(cls):
        return cls._get_option(OptionKeys.smtp_config)

    @smtp_config.setter
    def smtp_config(cls, value):
        cls._set_option(OptionKeys.smtp_config, value)

    @my_property
    def judge_server_token(cls):
        return cls._get_option(OptionKeys.judge_server_token)

    @judge_server_token.setter
    def judge_server_token(cls, value):
        cls._set_option(OptionKeys.judge_server_token, value)

    @my_property
    def throttling(cls):
        return cls._get_option(OptionKeys.throttling)

    @throttling.setter
    def throttling(cls, value):
        cls._set_option(OptionKeys.throttling, value)

    @my_property(ttl=DEFAULT_SHORT_TTL)
    def languages(cls):
        return cls._get_option(OptionKeys.languages)

    @languages.setter
    def languages(cls, value):
        cls._set_option(OptionKeys.languages, value)

    @my_property(ttl=DEFAULT_SHORT_TTL)
    def spj_languages(cls):
        return [item for item in cls.languages if "spj" in item]

    @my_property(ttl=DEFAULT_SHORT_TTL)
    def language_names(cls):
        return [item["name"] for item in cls.languages]

    @my_property(ttl=DEFAULT_SHORT_TTL)
    def spj_language_names(cls):
        return [item["name"] for item in cls.languages if "spj" in item]

    def reset_languages(cls):
        cls.languages = languages


class SysOptions(metaclass=_SysOptionsMeta):
    pass
