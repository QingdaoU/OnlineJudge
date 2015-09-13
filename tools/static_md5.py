# coding=utf-8
import hashlib
import re
import os
import shutil

template_src_path = "template/src/"
template_release_path = "template/release/"

static_src_path = "static/src/"
static_release_path = "static/release/"

# 删除模板的 release 文件夹
shutil.rmtree(template_release_path)
# 复制一份模板文件夹到 release
shutil.copytree(template_src_path, template_release_path)

# 删除静态文件的 release 文件夹
shutil.rmtree(static_release_path)
# 复制一份静态文件文件夹到 release
shutil.copytree(static_src_path, static_release_path)

r = re.compile(r'<script src="(.+)"></script>')

name_map = {}


def do(match):
    js_path = match.group(1).lstrip("/static/")

    if not os.path.exists(static_release_path + js_path):
        return match.group(0)

    if js_path in name_map:
        md5 = name_map[js_path]
    else:
        # rename
        md5 = hashlib.md5(open(static_release_path + js_path, "r").read()).hexdigest()
        os.rename(static_release_path + js_path, static_release_path + js_path + "?v=" + md5)
    return '<script src="%s"></script>' % (js_path + "?v=" + md5,)


for root, dirs, files in os.walk(template_release_path):
    for name in files:
        html_path = os.path.join(root, name)
        html_content = open(html_path, "r").read()
        replaced_html_content = re.sub(r, do, html_content)

        f = open(html_path, "w")
        f.write(replaced_html_content)
        f.close()
