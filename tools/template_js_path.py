# coding=utf-8
import json
import re
import os
import logging


logger = logging.getLogger('runserver_info')

template_src_path = "template/src/"

total_file = []
module_list = []

logger.info("\n\n-------------\n\n")
logger.info(u"        //以下都是页面 script 标签引用的js")

for root, dirs, files in os.walk(template_src_path):
    for name in files:
        html_path = os.path.join(root, name)
        html_content = open(html_path, "r").read()
        r = re.findall(re.compile('<script src="(.*)"></script>'), html_content)
        if r:
            for item in r:
                if item and "app" in item:
                    total_file.append(item)

i = 0
for item in set(total_file):
    module_name = item.replace("/static/js/", "").split("/")[-1].replace(".js", "") + "_" + str(i)

    module_list.append(module_name)
    logger.info("        " +
                module_name + "_pack" +
                ": \"" + item.replace("/static/js/", "").replace(".js", "") +
                "\",")
    i += 1

logger.info("\n\n-------------\n\n")

result = []
for item in module_list:
    result.append({"name": item + "_pack"})

logger.info(json.dumps(result, indent=4, separators=(',', ': ')))
