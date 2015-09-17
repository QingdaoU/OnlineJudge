# coding=utf-8
import hashlib
import re
import os
import shutil

template_src_path = "template/src/"
template_release_path = "template/release/"

static_src_path = "static/src/"
static_release_path = "static/release/"

print "Begin to compress js"
if os.system("node static/src/js/r.js -o static/src/js/build.js"):
    print "Failed to compress js, exit"
    exit()

try:
    # 删除模板的 release 文件夹
    shutil.rmtree(template_release_path)
except Exception:
    pass
# 复制一份模板文件夹到 release
shutil.copytree(template_src_path, template_release_path)

# 删除静态文件的 release 文件夹
# shutil.rmtree(static_release_path)
# 复制一份静态文件文件夹到 release
# shutil.copytree(static_src_path, static_release_path)

js_re = re.compile(r'<script src="(.+)"></script>')
css_re = re.compile(r'<link href="(.+)" rel="stylesheet">')

name_map = {}


def process(match):
    file_path = match.group(1).replace("/static/", "")

    if not os.path.exists(static_release_path + file_path):
        return match.group(0)

    if file_path in name_map:
        md5 = name_map[file_path]
    else:
        # rename
        md5 = hashlib.md5(open(static_release_path + file_path, "r").read()).hexdigest()
        # os.rename(static_release_path + js_path, static_release_path + js_path + "?v=" + md5)
    if ".js" in file_path:
        return '<script src="/static/%s"></script>' % (file_path + "?v=" + md5[:6], )
    elif ".css" in file_path:
        return '<link rel="stylesheet" type="text/css" href="/static/%s">' % (file_path + "?v=" + md5[:6], )
    else:
        return match.group(0)


print "Begin to add md5 stamp in html"
for root, dirs, files in os.walk(template_release_path):
    for name in files:
        html_path = os.path.join(root, name)
        print "Processing: " + html_path
        html_content = open(html_path, "r").read()
        js_replaced_html_content = re.sub(js_re, process, html_content)
        css_replaced_html_content = re.sub(css_re, process, js_replaced_html_content)

        f = open(html_path, "w")
        f.write(css_replaced_html_content)
        f.close()

print "Done"
