from django.db import models
from utils.models import RichTextField
from account.models import User
from problem.models import Problem


class LessonPlan(models.Model):
    title = models.TextField()
    description = models.TextField(null=True)
    content = RichTextField()
    pdf_file = models.TextField(null=True)
    cover_image = models.TextField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)
    visible = models.BooleanField(default=True)
    problems = models.ManyToManyField(Problem, through='LessonPlanProblem', related_name='lesson_plans')

    class Meta:
        db_table = "lesson_plan"
        ordering = ("-create_time",)

    def __str__(self):
        return self.title


class LessonPlanProblem(models.Model):
    lesson_plan = models.ForeignKey(LessonPlan, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = "lesson_plan_problem"
        ordering = ("order",)
        unique_together = (("lesson_plan", "problem"),)
