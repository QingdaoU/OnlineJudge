# coding=utf-8
from django.db import models

from account.models import User
from utils.models import RichTextField


class ProblemTag(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        db_table = "problem_tag"


class AbstractProblem(models.Model):
    # 标题
    title = models.CharField(max_length=50)
    # 问题描述 HTML 格式
    description = RichTextField()
    # 输入描述
    input_description = models.CharField(max_length=10000)
    # 输出描述
    output_description = models.CharField(max_length=10000)
    # 样例输入 可能会存储 json 格式的数据
    samples = models.TextField(blank=True)
    # 测试用例id 这个id 可以用来拼接得到测试用例的文件存储位置
    test_case_id = models.CharField(max_length=40)
    # 提示
    hint = RichTextField(blank=True, null=True)
    # 创建时间
    create_time = models.DateTimeField(auto_now_add=True)
    # 最后更新时间，不适用auto_now，因为本 model 里面的提交数量是变化的，导致每次 last_update_time 也更新了
    # 需要每次编辑后手动赋值
    last_update_time = models.DateTimeField(blank=True, null=True)
    # 这个题是谁创建的
    created_by = models.ForeignKey(User)
    # 时间限制 单位是毫秒
    time_limit = models.IntegerField()
    # 内存限制 单位是MB
    memory_limit = models.IntegerField()
    # special judge
    spj = models.BooleanField(default=False)
    spj_language = models.IntegerField(blank=True, null=True)
    spj_code = models.TextField(blank=True, null=True)
    spj_version = models.CharField(max_length=32, blank=True, null=True)
    # 是否可见 false的话相当于删除
    visible = models.BooleanField(default=True)
    # 总共提交数量
    total_submit_number = models.IntegerField(default=0)
    # 通过数量
    total_accepted_number = models.IntegerField(default=0)

    class Meta:
        db_table = "problem"
        abstract = True

    def add_submission_number(self):
        self.total_submit_number += 1
        self.save(update_fields=["total_submit_number"])

    def add_ac_number(self):
        self.total_accepted_number += 1
        self.save(update_fields=["total_accepted_number"])


class Problem(AbstractProblem):
    # 难度 0 - n
    difficulty = models.IntegerField()
    # 标签
    tags = models.ManyToManyField(ProblemTag)
    # 来源
    source = models.CharField(max_length=200, blank=True, null=True)
