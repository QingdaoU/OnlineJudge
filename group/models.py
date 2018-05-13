from django.db import models
from account.models import User


class Group(models.Model):
    name = models.TextField(unique=True)
    description = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    password = models.TextField()
    allow_join = models.BooleanField()
    created_by = models.ForeignKey(User, related_name="my_groups")
    members = models.ManyToManyField(User)

    class Meta:
        db_table = "group"
