# flake8: noqa
import os
import sys
import re
import json
import django
import hashlib
from json.decoder import JSONDecodeError

sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oj.settings")
django.setup()
from django.conf import settings
from account.models import User, UserProfile, AdminType, ProblemPermission
from problem.models import Problem, ProblemTag, ProblemDifficulty, ProblemRuleType

admin_type_map = {
    0: AdminType.REGULAR_USER,
    1: AdminType.ADMIN,
    2: AdminType.SUPER_ADMIN
}
languages_map = {
    1: "C",
    2: "C++",
    3: "Java"
}
email_regex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

# pk -> name
tags = {}
# pk -> user obj
users = {}

problems = []


def get_input_result():
    while True:
        resp = input()
        if resp not in ["yes", "no"]:
            print("Please input yes or no")
            continue
        return resp == "yes"


def set_problem_display_id_prefix():
    while True:
        print("Please input a prefix which will be used in all the imported problem's displayID")
        print(
            "For example, if your input is 'old'(no quote), the problems' display id will be old1, old2, old3..\ninput:",
            end="")
        resp = input()
        if resp.strip():
            return resp.strip()
        else:
            print("Empty prefix detected, sure to do that? (yes/no)")
            if get_input_result():
                return ""


def get_stripped_output_md5(test_case_id, output_name):
    output_path = os.path.join(settings.TEST_CASE_DIR, test_case_id, output_name)
    with open(output_path, 'r') as f:
        return hashlib.md5(f.read().rstrip().encode('utf-8')).hexdigest()


def get_test_case_score(test_case_id):
    info_path = os.path.join(settings.TEST_CASE_DIR, test_case_id, "info")
    if not os.path.exists(info_path):
        return []
    with open(info_path, "r") as info_file:
        info = json.load(info_file)
    test_case_score = []
    need_rewrite = True
    for test_case in info["test_cases"].values():
        if test_case.__contains__("stripped_output_md5"):
            need_rewrite = False
        elif test_case.__contains__("striped_output_md5"):
            test_case["stripped_output_md5"] = test_case.pop("striped_output_md5")
        else:
            test_case["stripped_output_md5"] = get_stripped_output_md5(test_case_id, test_case["output_name"])
        test_case_score.append({"input_name": test_case["input_name"],
                                "output_name": test_case.get("output_name", "-"),
                                "score": 0})
    if need_rewrite:
        with open(info_path, "w") as f:
            f.write(json.dumps(info))
    return test_case_score


def import_users():
    i = 0
    print("Find %d users in old data." % len(users.keys()))
    print("import users now? (yes/no)")
    if get_input_result():
        for data in users.values():
            if not email_regex.match(data["email"]):
                print("%s will not be created due to invalid email: %s" % (data["username"], data["email"]))
                continue
            data["username"] = data["username"].lower()
            user, created = User.objects.get_or_create(username=data["username"])
            if not created:
                print("%s already exists, omitted" % user.username)
                continue
            user.password = data["password"]
            user.email = data["email"]
            admin_type = admin_type_map[data["admin_type"]]
            user.admin_type = admin_type
            if admin_type == AdminType.ADMIN:
                user.problem_permission = ProblemPermission.OWN
            elif admin_type == AdminType.SUPER_ADMIN:
                user.problem_permission = ProblemPermission.ALL
            user.save()
            UserProfile.objects.create(user=user, real_name=data["real_name"])
            i += 1
            print("%s imported successfully" % user.username)
        print("%d users have successfully imported\n" % i)


def import_tags():
    i = 0
    print("\nFind these tags in old data:")
    print(", ".join(tags.values()), '\n')
    print("import tags now? (yes/no)")
    if get_input_result():
        for tagname in tags.values():
            tag, created = ProblemTag.objects.get_or_create(name=tagname)
            if not created:
                print("%s already exists, omitted" % tagname)
            else:
                print("%s tag created successfully" % tagname)
                i += 1
        print("%d tags have successfully imported\n" % i)
    else:
        print("Problem depends on problem_tags and users, exit..")
        exit(1)


def import_problems():
    i = 0
    print("\nFind %d problems in old data" % len(problems))
    prefix = set_problem_display_id_prefix()
    print("import problems using prefix: %s? (yes/no)" % prefix)
    if get_input_result():
        default_creator = User.objects.first()
        for data in problems:
            data["_id"] = prefix + str(data.pop("id"))
            if Problem.objects.filter(_id=data["_id"]).exists():
                print("%s has the same display_id with the db problem" % data["title"])
                continue
            try:
                creator_id = \
                    User.objects.filter(username=users[data["created_by"]]["username"]).values_list("id", flat=True)[0]
            except (User.DoesNotExist, IndexError):
                print("The origin creator does not exist, set it to default_creator")
                creator_id = default_creator.id
            data["created_by_id"] = creator_id
            data.pop("created_by")
            data["difficulty"] = ProblemDifficulty.Mid
            if data["spj_language"]:
                data["spj_language"] = languages_map[data["spj_language"]]
            data["samples"] = json.loads(data["samples"])
            data["languages"] = ["C", "C++"]
            test_case_score = get_test_case_score(data["test_case_id"])
            if not test_case_score:
                print("%s test_case files don't exist, omitted" % data["title"])
                continue
            data["test_case_score"] = test_case_score
            data["rule_type"] = ProblemRuleType.ACM
            data["template"] = {}
            data.pop("total_submit_number")
            data.pop("total_accepted_number")
            tag_ids = data.pop("tags")
            problem = Problem.objects.create(**data)
            problem.create_time = data["create_time"]
            problem.save()
            for tag_id in tag_ids:
                tag, _ = ProblemTag.objects.get_or_create(name=tags[tag_id])
                problem.tags.add(tag)
            i += 1
            print("%s imported successfully" % data["title"])
    print("%d problems have successfully imported" % i)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: python3 %s [old_data_path]" % sys.argv[0])
        exit(0)
    data_path = sys.argv[1]
    if not os.path.isfile(data_path):
        print("Data file does not exist")
        exit(1)

    try:
        with open(data_path, "r") as data_file:
            old_data = json.load(data_file)
    except JSONDecodeError:
        print("Data file format error, ensure it's a valid json file!")
        exit(1)
    print("Read old data successfully.\n")

    for obj in old_data:
        if obj["model"] == "problem.problemtag":
            tags[obj["pk"]] = obj["fields"]["name"]
        elif obj["model"] == "account.user":
            users[obj["pk"]] = obj["fields"]
        elif obj["model"] == "problem.problem":
            obj["fields"]["id"] = obj["pk"]
            problems.append(obj["fields"])
    import_users()
    import_tags()
    import_problems()
