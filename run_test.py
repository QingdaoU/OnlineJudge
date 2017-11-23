import getopt
import os
import sys

opts, args = getopt.getopt(sys.argv[1:], "cm:", ["coverage=", "module="])

is_coverage = False
test_module = ""
setting = "oj.settings"

for opt, arg in opts:
    if opt in ["-c", "--coverage"]:
        is_coverage = True
    if opt in ["-m", "--module"]:
        test_module = arg

print("Coverage: {cov}".format(cov=is_coverage))
print("Module: {mod}".format(mod=(test_module if test_module else "All")))

print("running flake8...")
if os.system("flake8 --statistics ."):
    exit()

ret = os.system("coverage run --include=\"$PWD/*\" manage.py test {module} --settings={setting}".format(module=test_module, setting=setting))

if not ret and is_coverage:
    os.system("coverage html && open htmlcov/index.html")
