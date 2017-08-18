"""
Copyright 2017 TY<master@t-y.me>
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
import random
from math import ceil
from six import BytesIO
from PIL import Image, ImageDraw, ImageFont

__version__ = '0.3.3'
current_path = os.path.normpath(os.path.dirname(__file__))

class Captcha(object):

    def __init__(self, request):
        """ something init
        """

        self.django_request = request
        self.session_key = '_django_captcha_key'
        self.words = ["hello", "word"]

        # image size (pix)
        self.img_width = 150
        self.img_height = 30

        self.type = 'number'
        self.mode = 'number'

    def _get_font_size(self):
        s1 = int(self.img_height * 0.8)
        s2 = int(self.img_width/len(self.code))
        return int(min((s1, s2)) + max((s1, s2))*0.05)

    def _get_words(self):
        """  words list
        """

        # TODO  扩充单词表

        if self.words:
            return set(self.words)


    def _set_answer(self, answer):
        self.django_request.session[self.session_key] = str(answer)

    def _generate(self):
        # 英文单词验证码
        def word():
            code = random.sample(self._get_words(), 1)[0]
            self._set_answer(code)
            return code

        # 数字公式验证码
        def number():
            m, n = 1, 50
            x = random.randrange(m, n)
            y = random.randrange(m, n)

            r = random.randrange(0, 2)
            if r == 0:
                code = "%s - %s = ?" % (x, y)
                z = x - y
            else:
                code = "%s + %s = ?" % (x, y)
                z = x + y
            self._set_answer(z)
            return code

        fun = eval(self.mode.lower())
        return fun()

    def get(self):
        """ return captcha image bytes
        """

        # font color
        self.font_color = ['black', 'darkblue', 'darkred']

        # background color
        self.background = (random.randrange(230, 255), random.randrange(230, 255), random.randrange(230, 255))

        # font path
        self.font_path = os.path.join(current_path, 'timesbi.ttf')  # or Menlo.ttc

        self.django_request.session[self.session_key] = ''
        im = Image.new('RGB', (self.img_width, self.img_height), self.background)
        self.code = self._generate()

        # set font size automaticly
        self.font_size = self._get_font_size()

        # creat
        draw = ImageDraw.Draw(im)

        # draw noisy point/line
        if self.mode == 'word':
            c = int(8/len(self.code)*3) or 3
        elif self.mode == 'number':
            c = 4

        for i in range(random.randrange(c-2, c)):
            line_color = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
            xy = (random.randrange(0, int(self.img_width*0.2)), random.randrange(0, self.img_height),
            random.randrange(int(3*self.img_width/4), self.img_width), random.randrange(0, self.img_height))
            draw.line(xy, fill=line_color, width=int(self.font_size*0.1))

        # main part
        j = int(self.font_size*0.3)
        k = int(self.font_size*0.5)
        x = random.randrange(j, k)

        for i in self.code:
            # 上下抖动量,字数越多,上下抖动越大
            m = int(len(self.code))
            y = random.randrange(1, 3)

            if i in ('+', '=', '?'):
                # 对计算符号等特殊字符放大处理
                m = ceil(self.font_size*0.8)
            else:
                # 字体大小变化量,字数越少,字体大小变化越多
                m = random.randrange(0, int(45 / self.font_size) + int(self.font_size/5))

            self.font = ImageFont.truetype(self.font_path.replace('\\', '/'), self.font_size + int(ceil(m)))
            draw.text((x, y), i, font=self.font, fill=random.choice(self.font_color))
            x += self.font_size*0.9

        del x
        del draw
        with BytesIO() as buf:
            im.save(buf, 'gif')
            buf_str = buf.getvalue()
        return buf_str

    def validate(self, code):
        """ user input validate
        """

        if not code:
            return False

        code = code.strip()
        _code = self.django_request.session.get(self.session_key) or ''
        self.django_request.session[self.session_key] = ''
        return _code.lower() == str(code).lower()

