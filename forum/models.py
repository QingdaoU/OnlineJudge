from django.db import models

from account.models import User
from utils.models import RichTextField


class ForumPost(models.Model):
    title = models.TextField()
    sort = models.IntegerField()
    # HTML
    content = RichTextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)
    is_top = models.BooleanField(default=False)
    is_nice = models.BooleanField(default=False)
    is_light = models.BooleanField(default=False)

    class Meta:
        db_table = "forumPost"
        ordering = ("-create_time",)


class ForumReply(models.Model):
    fa_id = models.IntegerField()
    # HTML
    content = RichTextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    floor = models.IntegerField()

    class Meta:
        db_table = "forumReply"
        ordering = ("floor",)
