# -*- coding: utf-8 -*-
"""
Python 富文本XSS过滤类
@package XssHtml
@version 0.1
@link http://phith0n.github.io/python-xss-filter
@since 20150407
@copyright (c) Phithon All Rights Reserved

Based on native Python module HTMLParser purifier of HTML, To Clear all javascript in html
You can use it in all python web framework
Written by Phithon <root@leavesongs.com> in 2015 and placed in the public domain.
phithon <root@leavesongs.com> 编写于20150407
From: XDSEC <www.xdsec.org> & 离别歌 <www.leavesongs.com>
GitHub Pages: https://github.com/phith0n/python-xss-filter
Usage:
    parser = XssHtml()
    parser.feed('<html code>')
    parser.close()
    html = parser.getHtml()
    print html

Requirements
Python 2.6+ or 3.2+
Cannot defense xss in browser which is belowed IE7
浏览器版本：IE7+ 或其他浏览器，无法防御IE6及以下版本浏览器中的XSS
"""
import re

try:
    from html.parser import HTMLParser
except:
    from HTMLParser import HTMLParser


class XssHtml(HTMLParser):
    allow_tags = ['a', 'img', 'br', 'strong', 'b', 'code', 'pre',
                  'p', 'div', 'em', 'span', 'h1', 'h2', 'h3', 'h4',
                  'h5', 'h6', 'blockquote', 'ul', 'ol', 'tr', 'th', 'td',
                  'hr', 'li', 'u', 'embed', 's', 'table', 'thead', 'tbody',
                  'caption', 'small', 'q', 'sup', 'sub', 'font']
    common_attrs = ["style", "class", "name"]
    nonend_tags = ["img", "hr", "br", "embed"]
    tags_own_attrs = {
        "img": ["src", "width", "height", "alt", "align"],
        "a": ["href", "target", "rel", "title"],
        "embed": ["src", "width", "height", "type", "allowfullscreen", "loop", "play", "wmode", "menu"],
        "table": ["border", "cellpadding", "cellspacing"],
        "font": ["color"]
    }

    def __init__(self, allows=[]):
        HTMLParser.__init__(self)
        self.allow_tags = allows if allows else self.allow_tags
        self.result = []
        self.start = []
        self.data = []

    def getHtml(self):
        """
        Get the safe html code
        """
        for i in range(0, len(self.result)):
            if self.result[i].strip('\n'):
                self.data.append(self.result[i])
        return ''.join(self.data)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_starttag(self, tag, attrs):
        if tag not in self.allow_tags:
            return
        end_diagonal = ' /' if tag in self.nonend_tags else ''
        if not end_diagonal:
            self.start.append(tag)
        attdict = {}
        for attr in attrs:
            attdict[attr[0]] = attr[1]

        attdict = self._wash_attr(attdict, tag)
        if hasattr(self, "node_%s" % tag):
            attdict = getattr(self, "node_%s" % tag)(attdict)
        else:
            attdict = self.node_default(attdict)

        attrs = []
        for (key, value) in attdict.items():
            attrs.append('%s="%s"' % (key, self._htmlspecialchars(value)))
        attrs = (' ' + ' '.join(attrs)) if attrs else ''
        self.result.append('<' + tag + attrs + end_diagonal + '>')

    def handle_endtag(self, tag):
        if self.start and tag == self.start[len(self.start) - 1]:
            self.result.append('</' + tag + '>')
            self.start.pop()

    def handle_data(self, data):
        self.result.append(self._htmlspecialchars(data))

    def handle_entityref(self, name):
        if name.isalpha():
            self.result.append("&%s;" % name)

    def handle_charref(self, name):
        if name.isdigit():
            self.result.append("&#%s;" % name)

    def node_default(self, attrs):
        attrs = self._common_attr(attrs)
        return attrs

    def node_a(self, attrs):
        attrs = self._common_attr(attrs)
        attrs = self._get_link(attrs, "href")
        attrs = self._set_attr_default(attrs, "target", "_blank")
        attrs = self._limit_attr(attrs, {
            "target": ["_blank", "_self"]
        })
        return attrs

    def node_embed(self, attrs):
        attrs = self._common_attr(attrs)
        attrs = self._get_link(attrs, "src")
        attrs = self._limit_attr(attrs, {
            "type": ["application/x-shockwave-flash"],
            "wmode": ["transparent", "window", "opaque"],
            "play": ["true", "false"],
            "loop": ["true", "false"],
            "menu": ["true", "false"],
            "allowfullscreen": ["true", "false"]
        })
        attrs["allowscriptaccess"] = "never"
        attrs["allownetworking"] = "none"
        return attrs

    def _true_url(self, url):
        prog = re.compile(r"^(http|https|ftp)://.+", re.I | re.S)
        if prog.match(url):
            return url
        else:
            return "http://%s" % url

    def _true_style(self, style):
        if style:
            style = re.sub(r"(\\|&#|/\*|\*/)", "_", style)
            style = re.sub(r"e.*x.*p.*r.*e.*s.*s.*i.*o.*n", "_", style)
        return style

    def _get_style(self, attrs):
        if "style" in attrs:
            attrs["style"] = self._true_style(attrs.get("style"))
        return attrs

    def _get_link(self, attrs, name):
        if name in attrs:
            attrs[name] = self._true_url(attrs[name])
        return attrs

    def _wash_attr(self, attrs, tag):
        if tag in self.tags_own_attrs:
            other = self.tags_own_attrs.get(tag)
        else:
            other = []
        if attrs:
            for (key, value) in attrs.items():
                if key not in self.common_attrs + other:
                    del attrs[key]
        return attrs

    def _common_attr(self, attrs):
        attrs = self._get_style(attrs)
        return attrs

    def _set_attr_default(self, attrs, name, default=''):
        if name not in attrs:
            attrs[name] = default
        return attrs

    def _limit_attr(self, attrs, limit={}):
        for (key, value) in limit.items():
            if key in attrs and attrs[key] not in value:
                del attrs[key]
        return attrs

    def _htmlspecialchars(self, html):
        return html.replace("<", "&lt;") \
            .replace(">", "&gt;") \
            .replace('"', "&quot;") \
            .replace("'", "&#039;")


if "__main__" == __name__:
    parser = XssHtml()
    parser.feed("""<p><img src=1 onerror=alert(/xss/)></p><div class="left">
        <a href='javascript:prompt(1)'><br />hehe</a></div>
        <p id="test" onmouseover="alert(1)">&gt;M<svg>
        <a href="https://www.baidu.com" target="self">MM</a></p>
        <embed src='javascript:alert(/hehe/)' allowscriptaccess=always />""")
    parser.close()
    print(parser.getHtml())
