import os
from django.core.cache import cache
from django.db import transaction, IntegrityError

from utils.constants import CacheKey
from utils.shortcuts import rand_str
from .models import SysOptions as SysOptionsModel


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


class _SysOptionsMeta(type):
    @classmethod
    def _set_cache(mcs, option_key, option_value):
        cache.set(f"{CacheKey.option}:{option_key}", option_value, timeout=60)

    @classmethod
    def _del_cache(mcs, option_key):
        cache.delete(f"{CacheKey.option}:{option_key}")

    @classmethod
    def _get_keys(cls):
        return [key for key in OptionKeys.__dict__ if not key.startswith("__")]

    def rebuild_cache(cls):
        for key in cls._get_keys():
            # get option 的时候会写 cache 的
            cls._get_option(key, use_cache=False)

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
    def _get_option(mcs, option_key, use_cache=True):
        try:
            if use_cache:
                option = cache.get(f"{CacheKey.option}:{option_key}")
                if option:
                    return option
            option = SysOptionsModel.objects.get(key=option_key)
            value = option.value
            mcs._set_cache(option_key, value)
            return value
        except SysOptionsModel.DoesNotExist:
            mcs._init_option()
            return mcs._get_option(option_key, use_cache=use_cache)

    @classmethod
    def _set_option(mcs, option_key: str, option_value):
        try:
            with transaction.atomic():
                option = SysOptionsModel.objects.select_for_update().get(key=option_key)
                option.value = option_value
                option.save()
                mcs._del_cache(option_key)
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
                mcs._del_cache(option_key)
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

    @property
    def website_base_url(cls):
        return cls._get_option(OptionKeys.website_base_url)

    @website_base_url.setter
    def website_base_url(cls, value):
        cls._set_option(OptionKeys.website_base_url, value)

    @property
    def website_name(cls):
        return cls._get_option(OptionKeys.website_name)

    @website_name.setter
    def website_name(cls, value):
        cls._set_option(OptionKeys.website_name, value)

    @property
    def website_name_shortcut(cls):
        return cls._get_option(OptionKeys.website_name_shortcut)

    @website_name_shortcut.setter
    def website_name_shortcut(cls, value):
        cls._set_option(OptionKeys.website_name_shortcut, value)

    @property
    def website_footer(cls):
        return cls._get_option(OptionKeys.website_footer)

    @website_footer.setter
    def website_footer(cls, value):
        cls._set_option(OptionKeys.website_footer, value)

    @property
    def allow_register(cls):
        return cls._get_option(OptionKeys.allow_register)

    @allow_register.setter
    def allow_register(cls, value):
        cls._set_option(OptionKeys.allow_register, value)

    @property
    def submission_list_show_all(cls):
        return cls._get_option(OptionKeys.submission_list_show_all)

    @submission_list_show_all.setter
    def submission_list_show_all(cls, value):
        cls._set_option(OptionKeys.submission_list_show_all, value)

    @property
    def smtp_config(cls):
        return cls._get_option(OptionKeys.smtp_config)

    @smtp_config.setter
    def smtp_config(cls, value):
        cls._set_option(OptionKeys.smtp_config, value)

    @property
    def judge_server_token(cls):
        return cls._get_option(OptionKeys.judge_server_token)

    @judge_server_token.setter
    def judge_server_token(cls, value):
        cls._set_option(OptionKeys.judge_server_token, value)

    @property
    def throttling(cls):
        return cls._get_option(OptionKeys.throttling)

    @throttling.setter
    def throttling(cls, value):
        cls._set_option(OptionKeys.throttling, value)


class SysOptions(metaclass=_SysOptionsMeta):
    pass
