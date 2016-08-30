# coding:utf-8

"""
Copyright 2013 TY<tianyu0915@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import time
import random
import StringIO
import logging

from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont


class Captcha(object):

    def __init__(self, request):
        """   
        初始化,设置各种属性
        """
        self.django_request = request
        self.session_key = '_django_captcha_key'
        self.captcha_expires_time = '_django_captcha_expires_time'

        # 验证码图片尺寸
        self.img_width = 90
        self.img_height = 30

    def _get_font_size(self, code):
        """  
        将图片高度的80%作为字体大小
        """
        s1 = int(self.img_height * 0.8)
        s2 = int(self.img_width / len(code))
        return int(min((s1, s2)) + max((s1, s2)) * 0.05)

    def _set_answer(self, answer):
        """  
        设置答案和过期时间
        """
        self.django_request.session[self.session_key] = str(answer)
        self.django_request.session[self.captcha_expires_time] = time.time() + 60

    def _make_code(self):
        """
        生成随机数或随机字符串
        """
        string = random.sample('abcdefghkmnpqrstuvwxyzABCDEFGHGKMNOPQRSTUVWXYZ23456789', 4)
        self._set_answer("".join(string))
        return string

    def display(self):
        """
        生成验证码图片
        """
        background = (random.randrange(200, 255), random.randrange(200, 255), random.randrange(200, 255))
        code_color = (random.randrange(0, 50), random.randrange(0, 50), random.randrange(0, 50), 255)

        font_path = os.path.join(os.path.normpath(os.path.dirname(__file__)), 'timesbi.ttf')

        image = Image.new('RGB', (self.img_width, self.img_height), background)
        code = self._make_code()
        font_size = self._get_font_size(code)
        draw = ImageDraw.Draw(image)

        # x是第一个字母的x坐标
        x = random.randrange(int(font_size * 0.3), int(font_size * 0.5))

        for i in code:
            # 字符y坐标
            y = random.randrange(1, 7)
            # 随机字符大小
            font = ImageFont.truetype(font_path.replace('\\', '/'), font_size + random.randrange(-3, 7))
            draw.text((x, y), i, font=font, fill=code_color)
            # 随机化字符之间的距离 字符粘连可以降低识别率
            x += font_size * random.randrange(6, 8) / 10

        buf = StringIO.StringIO()
        image.save(buf, 'gif')

        self.django_request.session[self.session_key] = "".join(code)
        return buf.getvalue()

    def check(self, code):
        """
        检查用户输入的验证码是否正确
        """
        _code = self.django_request.session.get(self.session_key) or ''
        if not _code:
            return False
        expires_time = self.django_request.session.get(self.captcha_expires_time) or 0
        # 注意 如果验证之后不清除之前的验证码的话 可能会造成重复验证的现象
        del self.django_request.session[self.session_key]
        del self.django_request.session[self.captcha_expires_time]
        if _code.lower() == str(code).lower() and time.time() < expires_time:
            return True
        else:
            return False
